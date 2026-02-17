"""
Graph of rule dependencies (GRD) with support for disjunctive heads.
"""

# References:
# - "Extending Decidable Cases for Rules with Existential Variables" —
#   Jean-Francois Baget, Michel Leclere, Marie-Laure Mugnier, Eric Salvat.
#   Link: https://www.ijcai.org/Proceedings/09/Papers/323.pdf
#
# Summary:
# The GRD captures dependencies between existential rules via unification
# conditions on heads and bodies. It is used to characterize decidable classes
# and to drive stratification and evaluation strategies.
#
# Properties used here:
# - Dependency edges encode potential rule triggering.
# - GRD-based criteria enable reasoning about termination and stratification.
#
# Implementation notes:
# This module constructs dependency edges using piece-unification and exposes
# them for stratification and evaluation procedures.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, TYPE_CHECKING

import igraph as ig  # type: ignore[import-untyped]
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.grd.dependency_checker import (
    DependencyChecker,
    ProductivityChecker,
)
from prototyping_inference_engine.grd.rule_utils import (
    ensure_safe_negation,
    extract_head_conjunction,
    extract_negative_body,
    extract_positive_body,
    split_head_disjuncts,
)
from prototyping_inference_engine.grd.stratification import Edge, StratificationStrategy
from prototyping_inference_engine.unifier.piece_unifier_algorithm import (
    PieceUnifierAlgorithm,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.kb.rule_base import RuleBase


@dataclass(frozen=True)
class GRDEdge:
    is_positive: bool


class DependencyComputationMode(Enum):
    UNIFIER = "unifier"
    PREDICATE = "predicate"
    HYBRID = "hybrid"


class GRD:
    def __init__(
        self,
        rules: Iterable[Rule],
        checkers: Iterable[DependencyChecker] | None = None,
        mode: DependencyComputationMode = DependencyComputationMode.UNIFIER,
    ):
        self._rules = tuple(rules)
        self._checkers = (
            tuple(checkers) if checkers is not None else (ProductivityChecker(),)
        )
        self._mode = mode
        self._edges: dict[Rule, dict[Rule, set[GRDEdge]]] = {}
        self._build()

    @property
    def rules(self) -> tuple[Rule, ...]:
        return self._rules

    @property
    def checkers(self) -> tuple[DependencyChecker, ...]:
        return self._checkers

    @property
    def mode(self) -> DependencyComputationMode:
        return self._mode

    def iter_edges(self) -> Iterable[Edge]:
        for src, targets in self._edges.items():
            for target, edges in targets.items():
                for edge in edges:
                    yield Edge(src=src, target=target, is_positive=edge.is_positive)

    def get_triggered_rules(self, src: Rule) -> set[Rule]:
        return {
            target
            for target, edges in self._edges.get(src, {}).items()
            if any(edge.is_positive for edge in edges)
        }

    def get_ancestor_rules(self, target: Rule) -> set[Rule]:
        ancestors: set[Rule] = set()
        to_process = [target]
        while to_process:
            current = to_process.pop()
            if current in ancestors:
                continue
            ancestors.add(current)
            for src, edges in self._edges.items():
                if current in edges and any(e.is_positive for e in edges[current]):
                    to_process.append(src)
        return ancestors

    def get_prevented_rules(self, src: Rule) -> set[Rule]:
        return {
            target
            for target, edges in self._edges.get(src, {}).items()
            if any(not edge.is_positive for edge in edges)
        }

    def is_stratifiable(self) -> bool:
        from prototyping_inference_engine.grd.stratification import is_stratifiable

        return is_stratifiable(self)

    def stratify(self, strategy: StratificationStrategy) -> Optional[list[RuleBase]]:
        return strategy.compute(self)

    def _build(self) -> None:
        self._edges = {r: {} for r in self._rules}
        if self._mode == DependencyComputationMode.PREDICATE:
            self._build_predicate_only()
            return
        if self._mode == DependencyComputationMode.HYBRID:
            self._build_hybrid()
            return
        self._build_unifier_only()

    def _build_unifier_only(self) -> None:
        index = _index_rules_by_body_predicate(self._rules)
        for r1 in self._rules:
            ensure_safe_negation(r1)
            for head_index, head_disjunct in enumerate(split_head_disjuncts(r1)):
                head_cq = extract_head_conjunction(head_disjunct)
                for pred in head_cq.atoms.predicates:
                    for r2 in index.get(pred, ()):
                        self._compute_dependencies_for_disjunct(r1, r2, head_index)

    def _build_predicate_only(self) -> None:
        for src, target, is_positive in _iter_predicate_edges(self._rules):
            self._edges[src].setdefault(target, set()).add(
                GRDEdge(is_positive=is_positive)
            )

    def _build_hybrid(self) -> None:
        rules = list(self._rules)
        rule_index = {rule: idx for idx, rule in enumerate(rules)}
        coarse_edges = list(_iter_predicate_edges(rules))

        graph = ig.Graph(directed=True)
        graph.add_vertices(len(rules))
        if coarse_edges:
            graph.add_edges(
                [
                    (rule_index[src], rule_index[target])
                    for src, target, _ in coarse_edges
                ]
            )

        membership = graph.connected_components(mode="STRONG").membership

        # Keep coarse cross-component edges and refine each component with unifiers.
        for src, target, is_positive in coarse_edges:
            if membership[rule_index[src]] != membership[rule_index[target]]:
                self._edges[src].setdefault(target, set()).add(
                    GRDEdge(is_positive=is_positive)
                )

        by_component: dict[int, list[Rule]] = {}
        for rule, comp_idx in zip(rules, membership):
            by_component.setdefault(comp_idx, []).append(rule)

        for component_rules in by_component.values():
            refined = GRD(
                component_rules,
                checkers=self._checkers,
                mode=DependencyComputationMode.UNIFIER,
            )
            for edge in refined.iter_edges():
                self._edges[edge.src].setdefault(edge.target, set()).add(
                    GRDEdge(is_positive=edge.is_positive)
                )

    def _compute_dependencies_for_disjunct(
        self, r1: Rule, r2: Rule, head_index: int
    ) -> None:
        ensure_safe_negation(r2)
        positive_body = extract_positive_body(r2)
        negative_body = extract_negative_body(r2)

        self._compute_dependency(r1, r2, head_index, positive_body, True)
        self._compute_dependency(r1, r2, head_index, negative_body, False)

    def _compute_dependency(
        self,
        r1: Rule,
        r2: Rule,
        head_index: int,
        target_body: ConjunctiveQuery,
        is_positive: bool,
    ) -> None:
        r1_head_rule = Rule.extract_conjunctive_rule(r1, head_index)
        r1_head_rule = _conjunctive_head_rule(r1_head_rule, r1)
        unifiers = PieceUnifierAlgorithm.compute_most_general_mono_piece_unifiers(
            target_body, r1_head_rule
        )

        for unifier in unifiers:
            if all(
                checker.is_valid_positive_dependency(r1_head_rule, r2, unifier)
                if is_positive
                else checker.is_valid_negative_dependency(r1_head_rule, r2, unifier)
                for checker in self._checkers
            ):
                self._edges[r1].setdefault(r2, set()).add(
                    GRDEdge(is_positive=is_positive)
                )
                return


def _index_rules_by_body_predicate(
    rules: Iterable[Rule],
) -> dict[Predicate, set[Rule]]:
    index: dict[Predicate, set[Rule]] = {}
    for rule in rules:
        positive_body = extract_positive_body(rule)
        negative_body = extract_negative_body(rule)
        for pred in positive_body.atoms.predicates | negative_body.atoms.predicates:
            index.setdefault(pred, set()).add(rule)
    return index


def _iter_predicate_edges(
    rules: Iterable[Rule],
) -> Iterable[tuple[Rule, Rule, bool]]:
    rules_seq = tuple(rules)
    index = _index_rules_by_body_predicate(rules_seq)
    seen: set[tuple[Rule, Rule, bool]] = set()

    for r1 in rules_seq:
        ensure_safe_negation(r1)
        for head_disjunct in split_head_disjuncts(r1):
            head_cq = extract_head_conjunction(head_disjunct)
            for pred in head_cq.atoms.predicates:
                for r2 in index.get(pred, ()):
                    ensure_safe_negation(r2)
                    positive = pred in extract_positive_body(r2).atoms.predicates
                    negative = pred in extract_negative_body(r2).atoms.predicates
                    if positive:
                        edge = (r1, r2, True)
                        if edge not in seen:
                            seen.add(edge)
                            yield edge
                    if negative:
                        edge = (r1, r2, False)
                        if edge not in seen:
                            seen.add(edge)
                            yield edge


def _conjunctive_head_rule(r1_head_rule: Rule, original_rule: Rule) -> Rule:
    positive_body = extract_positive_body(original_rule)
    atoms = list(positive_body.atoms)
    if not atoms:
        return r1_head_rule
    body_formula: Formula = atoms[0]
    for atom in atoms[1:]:
        body_formula = ConjunctionFormula(body_formula, atom)
    missing = body_formula.free_variables - r1_head_rule.head.free_variables
    for var in sorted(missing, key=str):
        body_formula = UniversalFormula(var, body_formula)
    return Rule(body_formula, r1_head_rule.head, r1_head_rule.label)
