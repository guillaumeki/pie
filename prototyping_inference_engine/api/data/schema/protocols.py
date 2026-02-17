"""Schema capability protocols."""

from typing import Iterable, Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.data.schema.model import RelationSchema


@runtime_checkable
class SchemaAware(Protocol):
    def get_schema(self, predicate: Predicate) -> RelationSchema | None: ...

    def get_schemas(self) -> Iterable[RelationSchema]: ...
