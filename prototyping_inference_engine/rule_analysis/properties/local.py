"""Local rule-property evaluators."""

from __future__ import annotations

from prototyping_inference_engine.rule_analysis.model import (
    PropertyId,
    PropertyResult,
    PropertyStatus,
)
from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot


def evaluate_linear(snapshot: AnalysisSnapshot) -> PropertyResult:
    unsupported = snapshot.unsupported_fragment_reason()
    if unsupported is not None:
        return PropertyResult(
            PropertyId.LINEAR, PropertyStatus.UNSUPPORTED, unsupported
        )

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
    unsupported = snapshot.unsupported_fragment_reason()
    if unsupported is not None:
        return PropertyResult(
            PropertyId.GUARDED,
            PropertyStatus.UNSUPPORTED,
            unsupported,
        )

    for rule in snapshot.rules:
        fragments = snapshot.fragments_by_rule[rule]
        body_variables = {
            variable for atom in fragments.positive_body for variable in atom.variables
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
    unsupported = snapshot.unsupported_fragment_reason()
    if unsupported is not None:
        return PropertyResult(
            PropertyId.FRONTIER_GUARDED,
            PropertyStatus.UNSUPPORTED,
            unsupported,
        )

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
    unsupported = snapshot.unsupported_fragment_reason()
    if unsupported is not None:
        return PropertyResult(
            PropertyId.RANGE_RESTRICTED,
            PropertyStatus.UNSUPPORTED,
            unsupported,
        )

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
