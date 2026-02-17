"""Session-level schema registry with compatibility validation."""

from __future__ import annotations

from typing import Iterable

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.data.schema.errors import (
    IncompatiblePredicateSchemaError,
)
from prototyping_inference_engine.api.data.schema.model import RelationSchema


class SessionSchemaRegistry:
    """Stores one canonical schema per predicate for a reasoning session."""

    def __init__(self, strict_position_names: bool = True):
        self._strict_position_names = strict_position_names
        self._schemas: dict[Predicate, RelationSchema] = {}

    @property
    def schemas(self) -> tuple[RelationSchema, ...]:
        return tuple(self._schemas.values())

    def get(self, predicate: Predicate) -> RelationSchema | None:
        return self._schemas.get(predicate)

    def register_or_validate(self, schema: RelationSchema) -> None:
        current = self._schemas.get(schema.predicate)
        if current is None:
            self._schemas[schema.predicate] = schema
            return

        if not current.is_compatible_with(
            schema, strict_position_names=self._strict_position_names
        ):
            raise IncompatiblePredicateSchemaError(
                schema.predicate,
                f"existing={current.positions}, incoming={schema.positions}",
            )

    def register_many(self, schemas: Iterable[RelationSchema]) -> None:
        for schema in schemas:
            self.register_or_validate(schema)
