"""Affected-position analysis for positive existential rules."""

# References:
# - "Data Exchange: Semantics and Query Answering" —
#   Ronald Fagin, Phokion G. Kolaitis, Renée J. Miller, Lucian Popa.
#   Link: https://research.ibm.com/publications/data-exchange-semantics-and-query-answering
# - "Query Answering under Non-guarded Rules in Datalog+/-" —
#   Andrea Calì, Georg Gottlob, Andreas Pieris.
#   Link: https://www.research.ed.ac.uk/en/publications/query-answering-under-non-guarded-rules-in-datalog/
#
# Summary:
# Affected positions approximate where existentially generated values may appear.
# The analysis starts from head positions carrying existential variables and
# propagates affectedness through frontier variables until reaching a fixpoint.
#
# Properties used here:
# - Initial existential head positions are affected.
# - If a frontier variable occurs in an affected body position, every head
#   position carrying that variable becomes affected.
#
# Implementation source:
# This module implements the affected-position fixpoint directly on PIE rules and
# normalized rule fragments instead of porting the legacy Integraal code.

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.rule_analysis.fragments import RuleFragments
from prototyping_inference_engine.rule_analysis.model import PredicatePosition


@dataclass(frozen=True)
class AffectedPositionSet:
    """Immutable set of affected predicate positions."""

    positions: frozenset[PredicatePosition]

    def contains(self, predicate: Predicate, position: int) -> bool:
        return PredicatePosition(predicate, position) in self.positions


def compute_affected_positions(
    rules: Iterable[Rule],
    fragments_by_rule: dict[Rule, RuleFragments],
) -> AffectedPositionSet:
    affected: set[PredicatePosition] = set()

    for rule in rules:
        fragments = fragments_by_rule[rule]
        for atom in fragments.all_head_atoms:
            for position, term in enumerate(atom.terms):
                if term in fragments.existential_variables:
                    affected.add(PredicatePosition(atom.predicate, position))

    changed = True
    while changed:
        changed = False
        for rule in rules:
            fragments = fragments_by_rule[rule]
            affected_frontier = {
                variable
                for variable in fragments.frontier
                if _variable_occurs_in_affected_body_position(
                    variable, fragments, affected
                )
            }
            for variable in affected_frontier:
                for head_position in _head_positions_for_variable(
                    variable, fragments.all_head_atoms
                ):
                    if head_position not in affected:
                        affected.add(head_position)
                        changed = True

    return AffectedPositionSet(frozenset(affected))


def _variable_occurs_in_affected_body_position(
    variable: Variable,
    fragments: RuleFragments,
    affected: set[PredicatePosition],
) -> bool:
    for atom in fragments.positive_body:
        for position, term in enumerate(atom.terms):
            if (
                term == variable
                and PredicatePosition(atom.predicate, position) in affected
            ):
                return True
    return False


def _head_positions_for_variable(
    variable: Variable,
    atoms: Iterable[Atom],
) -> tuple[PredicatePosition, ...]:
    positions: list[PredicatePosition] = []
    for atom in atoms:
        for position, term in enumerate(atom.terms):
            if term == variable:
                positions.append(PredicatePosition(atom.predicate, position))
    return tuple(positions)
