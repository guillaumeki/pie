"""Global rule-property evaluators."""

# References:
# - "Data Exchange: Semantics and Query Answering" — Ronald Fagin, Phokion G.
#   Kolaitis, Renée J. Miller, Lucian Popa.
#   Link: https://research.ibm.com/publications/data-exchange-semantics-and-query-answering
# - "Query Answering under Non-guarded Rules in Datalog+/-" — Andrea Calì,
#   Georg Gottlob, Andreas Pieris.
#   Link: https://www.research.ed.ac.uk/en/publications/query-answering-under-non-guarded-rules-in-datalog/
# - "Towards More Expressive Ontology Languages: The Query Answering Problem" —
#   Andrea Calì, Georg Gottlob, Andreas Pieris.
#   Link: https://www.research.ed.ac.uk/en/publications/towards-more-expressive-ontology-languages-the-query-answering-pr/
# - "Sticky Existential Rules and Disjunction are Incompatible" — Michael
#   Morak.
#   Link: https://proceedings.kr.org/2021/71/
#
# Summary:
# These evaluators classify rule-set properties derived from shared fixpoint
# data such as the position-dependency graph and marked-variable analysis.
#
# Properties used here:
# - Weak acyclicity is decided on the position-dependency graph, including all
#   head disjuncts.
# - Sticky and weakly-sticky reuse the marked-variable fixpoint and finite-rank
#   positions, but stay restricted to the classical positive non-disjunctive
#   fragment through property-specific applicability checks.
#
# Implementation source:
# This module composes PIE-native shared analyses and leaves fragment
# restrictions to the declarative property registry and analyser.

from __future__ import annotations

from prototyping_inference_engine.rule_analysis.marked_variables import (
    marked_variable_occurrences,
)
from prototyping_inference_engine.rule_analysis.model import (
    PropertyId,
    PropertyResult,
    PropertyStatus,
)
from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot


def evaluate_weakly_acyclic(snapshot: AnalysisSnapshot) -> PropertyResult:
    if snapshot.position_dependency_graph.is_weakly_acyclic():
        return PropertyResult(
            PropertyId.WEAKLY_ACYCLIC,
            PropertyStatus.SATISFIED,
            "The position-dependency graph has no strongly connected component with a special edge.",
        )

    return PropertyResult(
        PropertyId.WEAKLY_ACYCLIC,
        PropertyStatus.VIOLATED,
        "The position-dependency graph contains a special cycle.",
    )


def evaluate_sticky(snapshot: AnalysisSnapshot) -> PropertyResult:
    for marked_rule in snapshot.marked_variables.marked_rules:
        fragments = snapshot.fragments_by_rule[marked_rule.rule]
        for variable in marked_rule.marked_variables:
            occurrences = marked_variable_occurrences(fragments, variable)
            if len(occurrences) > 1:
                return PropertyResult(
                    PropertyId.STICKY,
                    PropertyStatus.VIOLATED,
                    (
                        f"Marked variable {variable} occurs {len(occurrences)} times "
                        f"in the body of rule {marked_rule.rule.label or marked_rule.rule}."
                    ),
                )

    return PropertyResult(
        PropertyId.STICKY,
        PropertyStatus.SATISFIED,
        "Every marked variable occurs at most once in every rule body.",
    )


def evaluate_weakly_sticky(snapshot: AnalysisSnapshot) -> PropertyResult:
    finite_rank_positions = snapshot.position_dependency_graph.finite_rank_positions
    for marked_rule in snapshot.marked_variables.marked_rules:
        fragments = snapshot.fragments_by_rule[marked_rule.rule]
        for variable in marked_rule.marked_variables:
            occurrences = marked_variable_occurrences(fragments, variable)
            if len(occurrences) <= 1:
                continue
            if not any(position in finite_rank_positions for position in occurrences):
                return PropertyResult(
                    PropertyId.WEAKLY_STICKY,
                    PropertyStatus.VIOLATED,
                    (
                        f"Repeated marked variable {variable} in rule "
                        f"{marked_rule.rule.label or marked_rule.rule} never occurs "
                        "at a finite-rank position."
                    ),
                )

    return PropertyResult(
        PropertyId.WEAKLY_STICKY,
        PropertyStatus.SATISFIED,
        "Every repeated marked variable occurs at some finite-rank position.",
    )
