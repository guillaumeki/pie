"""Schema model for predicate-backed relations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from prototyping_inference_engine.api.atom.predicate import Predicate


class LogicalType(Enum):
    UNKNOWN = "unknown"
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    IRI = "iri"


@dataclass(frozen=True)
class PositionSpec:
    name: str
    logical_type: LogicalType = LogicalType.UNKNOWN
    nullable: bool = False


@dataclass(frozen=True)
class RelationSchema:
    predicate: Predicate
    positions: tuple[PositionSpec, ...]

    def is_compatible_with(
        self, other: "RelationSchema", strict_position_names: bool = True
    ) -> bool:
        if self.predicate != other.predicate:
            return False
        if len(self.positions) != len(other.positions):
            return False

        for left, right in zip(self.positions, other.positions):
            if strict_position_names and left.name != right.name:
                return False
            if left.logical_type != right.logical_type:
                return False
            if left.nullable != right.nullable:
                return False

        return True
