"""Core value objects for rule analysis."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Mapping

from prototyping_inference_engine.api.atom.predicate import Predicate

if TYPE_CHECKING:
    from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot


@dataclass(frozen=True)
class PredicatePosition:
    """One predicate position identified by predicate and zero-based index."""

    predicate: Predicate
    position: int

    def __post_init__(self) -> None:
        if self.position < 0:
            raise ValueError("Predicate position must be non-negative.")
        if self.position >= self.predicate.arity:
            raise ValueError("Predicate position must be smaller than predicate arity.")

    @property
    def sort_key(self) -> tuple[str, int, int]:
        return (self.predicate.name, self.predicate.arity, self.position)

    def __str__(self) -> str:
        return f"{self.predicate.name}[{self.position}]"


@dataclass(frozen=True)
class PositionDependencyEdge:
    """Directed dependency edge between two predicate positions."""

    source: PredicatePosition
    target: PredicatePosition
    is_special: bool = False

    @property
    def sort_key(self) -> tuple[tuple[str, int, int], tuple[str, int, int], bool]:
        return (self.source.sort_key, self.target.sort_key, self.is_special)


class PropertyId(str, Enum):
    LINEAR = "linear"
    GUARDED = "guarded"
    FRONTIER_GUARDED = "frontier_guarded"
    RANGE_RESTRICTED = "range_restricted"
    WEAKLY_ACYCLIC = "weakly_acyclic"
    STICKY = "sticky"
    WEAKLY_STICKY = "weakly_sticky"


class PropertyStatus(str, Enum):
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class PropertyResult:
    """Structured result for one analysed rule property."""

    property_id: PropertyId
    status: PropertyStatus
    explanation: str = ""
    evidence: tuple[str, ...] = ()

    @property
    def is_satisfied(self) -> bool:
        return self.status == PropertyStatus.SATISFIED


@dataclass(frozen=True)
class AnalysisReport:
    """Final analyser output for a rule set."""

    snapshot: "AnalysisSnapshot"
    results: Mapping[PropertyId, PropertyResult]

    def get(self, property_id: PropertyId) -> PropertyResult:
        return self.results[property_id]

    @property
    def satisfied_properties(self) -> tuple[PropertyId, ...]:
        return tuple(
            property_id
            for property_id, result in self.results.items()
            if result.status == PropertyStatus.SATISFIED
        )
