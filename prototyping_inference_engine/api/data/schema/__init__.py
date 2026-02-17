"""Schema abstractions for typed predicate relations."""

from prototyping_inference_engine.api.data.schema.errors import (
    IncompatiblePredicateSchemaError,
)
from prototyping_inference_engine.api.data.schema.model import (
    LogicalType,
    PositionSpec,
    RelationSchema,
)
from prototyping_inference_engine.api.data.schema.protocols import SchemaAware
from prototyping_inference_engine.api.data.schema.session_registry import (
    SessionSchemaRegistry,
)

__all__ = [
    "LogicalType",
    "PositionSpec",
    "RelationSchema",
    "SchemaAware",
    "SessionSchemaRegistry",
    "IncompatiblePredicateSchemaError",
]
