"""Local rule-property evaluators."""

# References:
# - "A General Datalog-based Framework for Tractable Query Answering over
#   Ontologies" — Andrea Calì, Georg Gottlob, Thomas Lukasiewicz.
#   Link: https://www.iris.unina.it/handle/11588/950463
# - "Frontier-Guarded Existential Rules and Their Relationships" —
#   Jean-François Baget, Michel Leclère, Marie-Laure Mugnier, Eric Salvat.
#   Link: https://www.ijcai.org/Proceedings/11/Papers/126.pdf
# - "The Impact of Disjunction on Query Answering under Guarded-Based
#   Existential Rules" — Pierre Bourhis, Michael Morak, Andreas Pieris.
#   Link: https://www.ijcai.org/Proceedings/13/Papers/124.pdf
# - "Stable Model Semantics for Guarded Existential Rules and Description
#   Logics: Decidability and Complexity" — Georg Gottlob, André Hernich,
#   Clemens Kupke, Thomas Lukasiewicz.
#   Link: https://strathprints.strath.ac.uk/78886/
#
# Summary:
# These evaluators classify rule-local guarded-based fragments directly from
# PIE-native rule fragments. The implementation accepts disjunctive heads for
# body-based properties and interprets safe negation through positive guards.
#
# Properties used here:
# - Linearity is checked on the number of positive body atoms.
# - Guardedness requires one positive body atom covering every relevant body
#   variable, including variables that appear in safe negative literals.
# - Frontier-guardedness requires one positive body atom covering all frontier
#   variables.
# - Range restriction forbids existential head variables.
#
# Implementation source:
# This module implements PIE-native local property checks without copying the
# legacy Integraal analyser structure.

from __future__ import annotations

from prototyping_inference_engine.rule_analysis.model import (
    PropertyId,
    PropertyResult,
    PropertyStatus,
)
from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot


def evaluate_linear(snapshot: AnalysisSnapshot) -> PropertyResult:
    for rule in snapshot.rules:
        fragments = snapshot.fragments_by_rule[rule]
        if len(fragments.positive_body) != 1:
            return PropertyResult(
                PropertyId.LINEAR,
                PropertyStatus.VIOLATED,
                f"Rule {rule.label or rule} has {len(fragments.positive_body)} body atoms.",
            )
    return PropertyResult(
        PropertyId.LINEAR,
        PropertyStatus.SATISFIED,
        "Every rule has exactly one positive body atom.",
    )


def evaluate_guarded(snapshot: AnalysisSnapshot) -> PropertyResult:
    for rule in snapshot.rules:
        fragments = snapshot.fragments_by_rule[rule]
        body_variables = {
            variable
            for atom in (*fragments.positive_body, *fragments.negative_body)
            for variable in atom.variables
        }
        if not body_variables:
            continue
        if not any(
            body_variables.issubset(atom.variables) for atom in fragments.positive_body
        ):
            return PropertyResult(
                PropertyId.GUARDED,
                PropertyStatus.VIOLATED,
                f"Rule {rule.label or rule} has no guard atom covering all body variables.",
            )

    return PropertyResult(
        PropertyId.GUARDED,
        PropertyStatus.SATISFIED,
        "Every rule body contains a guard atom covering all body variables.",
    )


def evaluate_frontier_guarded(snapshot: AnalysisSnapshot) -> PropertyResult:
    for rule in snapshot.rules:
        fragments = snapshot.fragments_by_rule[rule]
        frontier = set(fragments.frontier)
        if not frontier:
            continue
        if not any(
            frontier.issubset(atom.variables) for atom in fragments.positive_body
        ):
            return PropertyResult(
                PropertyId.FRONTIER_GUARDED,
                PropertyStatus.VIOLATED,
                f"Rule {rule.label or rule} has no frontier guard atom.",
            )

    return PropertyResult(
        PropertyId.FRONTIER_GUARDED,
        PropertyStatus.SATISFIED,
        "Every rule has a body atom covering its frontier variables.",
    )


def evaluate_range_restricted(snapshot: AnalysisSnapshot) -> PropertyResult:
    for rule in snapshot.rules:
        if rule.existential_variables:
            return PropertyResult(
                PropertyId.RANGE_RESTRICTED,
                PropertyStatus.VIOLATED,
                f"Rule {rule.label or rule} has existential variables in the head.",
            )

    return PropertyResult(
        PropertyId.RANGE_RESTRICTED,
        PropertyStatus.SATISFIED,
        "No rule introduces existential head variables.",
    )
