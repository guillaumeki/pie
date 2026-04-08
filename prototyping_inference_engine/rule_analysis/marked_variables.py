"""Marked-variable analysis for sticky and weakly-sticky properties."""

# References:
# - "Towards More Expressive Ontology Languages: The Query Answering Problem" —
#   Andrea Calì, Georg Gottlob, Andreas Pieris.
#   Link: https://www.research.ed.ac.uk/en/publications/towards-more-expressive-ontology-languages-the-query-answering-pr/
# - "Query Answering under Non-guarded Rules in Datalog+/-" —
#   Andrea Calì, Georg Gottlob, Andreas Pieris.
#   Link: https://www.research.ed.ac.uk/en/publications/query-answering-under-non-guarded-rules-in-datalog/
#
# Summary:
# Sticky and weakly-sticky classes rely on a marking procedure over rule-body
# variables. Variables initially marked because they disappear from some head
# atom propagate through matching head positions until a fixpoint is reached.
#
# Properties used here:
# - Initial marks are body variables absent from at least one head atom.
# - Marked body positions propagate to head variables with the same predicate
#   position.
# - The final mark set is later checked for repeated body occurrences.
#
# Implementation source:
# This module implements the marking fixpoint directly on PIE-native fragments
# and keeps predicate identity exact, including arity.

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.rule_analysis.fragments import RuleFragments
from prototyping_inference_engine.rule_analysis.model import PredicatePosition


@dataclass(frozen=True)
class MarkedRule:
    """Marked variables for one rule."""

    rule: Rule
    marked_variables: frozenset[Variable]


@dataclass(frozen=True)
class MarkedVariableSet:
    """Immutable result of the marking procedure."""

    marked_rules: tuple[MarkedRule, ...]

    def marked_variables_for(self, rule: Rule) -> frozenset[Variable]:
        for marked_rule in self.marked_rules:
            if marked_rule.rule == rule:
                return marked_rule.marked_variables
        raise KeyError(f"Unknown rule: {rule}")


def compute_marked_variables(
    rules: Iterable[Rule],
    fragments_by_rule: dict[Rule, RuleFragments],
) -> MarkedVariableSet:
    rules_seq = tuple(rules)
    marks: dict[Rule, set[Variable]] = {rule: set() for rule in rules_seq}
    head_index: dict[Predicate, list[Rule]] = {}
    marked_positions: deque[PredicatePosition] = deque()

    for rule in rules_seq:
        fragments = fragments_by_rule[rule]
        for head_atom in fragments.all_head_atoms:
            head_index.setdefault(head_atom.predicate, []).append(rule)

    for rule in rules_seq:
        fragments = fragments_by_rule[rule]
        body_variables = {
            variable for atom in fragments.positive_body for variable in atom.variables
        }
        for variable in body_variables:
            if any(
                variable not in head_atom.variables
                for head_atom in fragments.all_head_atoms
            ):
                _mark_variable(
                    rule,
                    variable,
                    fragments,
                    marks,
                    marked_positions,
                )

    while marked_positions:
        position = marked_positions.popleft()
        for rule in head_index.get(position.predicate, ()):
            fragments = fragments_by_rule[rule]
            for head_atom in fragments.all_head_atoms:
                if head_atom.predicate != position.predicate:
                    continue
                head_term = head_atom.terms[position.position]
                if isinstance(head_term, Variable):
                    _mark_variable(
                        rule,
                        head_term,
                        fragments,
                        marks,
                        marked_positions,
                    )

    return MarkedVariableSet(
        tuple(
            MarkedRule(rule=rule, marked_variables=frozenset(marks[rule]))
            for rule in rules_seq
        )
    )


def _mark_variable(
    rule: Rule,
    variable: Variable,
    fragments: RuleFragments,
    marks: dict[Rule, set[Variable]],
    marked_positions: deque[PredicatePosition],
) -> None:
    if variable in marks[rule]:
        return

    marks[rule].add(variable)
    for atom in fragments.positive_body:
        for position, term in enumerate(atom.terms):
            if term == variable:
                marked_positions.append(PredicatePosition(atom.predicate, position))


def marked_variable_occurrences(
    fragments: RuleFragments,
    variable: Variable,
) -> tuple[PredicatePosition, ...]:
    occurrences: list[PredicatePosition] = []
    for atom in fragments.positive_body:
        for position, term in enumerate(atom.terms):
            if term == variable:
                occurrences.append(PredicatePosition(atom.predicate, position))
    return tuple(occurrences)
