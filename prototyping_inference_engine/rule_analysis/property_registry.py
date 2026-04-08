"""Declarative property registry for rule analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from prototyping_inference_engine.rule_analysis.model import (
    PropertyId,
    PropertyResult,
)
from prototyping_inference_engine.rule_analysis.properties.global_properties import (
    evaluate_sticky,
    evaluate_weakly_acyclic,
    evaluate_weakly_sticky,
)
from prototyping_inference_engine.rule_analysis.properties.local import (
    evaluate_frontier_guarded,
    evaluate_guarded,
    evaluate_linear,
    evaluate_range_restricted,
)
from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot


@dataclass(frozen=True)
class PropertySpec:
    """Metadata and evaluator for one property."""

    property_id: PropertyId
    full_name: str
    description: str
    evaluator: Callable[[AnalysisSnapshot], PropertyResult]
    implies: tuple[PropertyId, ...] = ()
    supports_negation: bool = True
    supports_disjunctive_head: bool = True


DEFAULT_PROPERTY_SPECS: tuple[PropertySpec, ...] = (
    PropertySpec(
        PropertyId.LINEAR,
        "Linear",
        "Every rule has a single positive body atom.",
        evaluate_linear,
        implies=(PropertyId.GUARDED, PropertyId.FRONTIER_GUARDED),
    ),
    PropertySpec(
        PropertyId.GUARDED,
        "Guarded",
        "Every rule body contains a positive atom covering all body variables.",
        evaluate_guarded,
        implies=(PropertyId.FRONTIER_GUARDED,),
    ),
    PropertySpec(
        PropertyId.FRONTIER_GUARDED,
        "Frontier guarded",
        "Every rule body contains a positive atom covering all frontier variables.",
        evaluate_frontier_guarded,
    ),
    PropertySpec(
        PropertyId.RANGE_RESTRICTED,
        "Range restricted",
        "No rule introduces existential head variables.",
        evaluate_range_restricted,
    ),
    PropertySpec(
        PropertyId.WEAKLY_ACYCLIC,
        "Weakly acyclic",
        "The position-dependency graph contains no special cycle.",
        evaluate_weakly_acyclic,
        implies=(PropertyId.WEAKLY_STICKY,),
    ),
    PropertySpec(
        PropertyId.STICKY,
        "Sticky",
        "Every marked variable occurs at most once in each rule body.",
        evaluate_sticky,
        implies=(PropertyId.WEAKLY_STICKY,),
        supports_negation=False,
        supports_disjunctive_head=False,
    ),
    PropertySpec(
        PropertyId.WEAKLY_STICKY,
        "Weakly sticky",
        "Every repeated marked variable occurs at some finite-rank position.",
        evaluate_weakly_sticky,
        supports_negation=False,
        supports_disjunctive_head=False,
    ),
)

DEFAULT_PROPERTY_REGISTRY: dict[PropertyId, PropertySpec] = {
    spec.property_id: spec for spec in DEFAULT_PROPERTY_SPECS
}
