"""
Graph of rule dependencies (GRD) with support for disjunctive heads.
"""

from dataclasses import dataclass
from typing import Iterable

from prototyping_inference_engine.api.atom.predicate import Predicate
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
from prototyping_inference_engine.unifier.piece_unifier_algorithm import (
    PieceUnifierAlgorithm,
)


@dataclass(frozen=True)
class GRDEdge:
    is_positive: bool


class GRD:
    def __init__(
        self,
        rules: Iterable[Rule],
        checkers: Iterable[DependencyChecker] | None = None,
    ):
        self._rules = tuple(rules)
        self._checkers = (
            tuple(checkers) if checkers is not None else (ProductivityChecker(),)
        )
        self._edges: dict[Rule, dict[Rule, set[GRDEdge]]] = {}
        self._build()

    @property
    def rules(self) -> tuple[Rule, ...]:
        return self._rules

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

    def _build(self) -> None:
        self._edges = {r: {} for r in self._rules}
        index = _index_rules_by_body_predicate(self._rules)
        for r1 in self._rules:
            ensure_safe_negation(r1)
            for head_index, head_disjunct in enumerate(split_head_disjuncts(r1)):
                head_cq = extract_head_conjunction(head_disjunct)
                for pred in head_cq.atoms.predicates:
                    for r2 in index.get(pred, ()):
                        self._compute_dependencies_for_disjunct(r1, r2, head_index)

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
