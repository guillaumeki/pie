"""
Data collection module for aggregating multiple data sources.

This module provides collection classes that aggregate multiple queryable
data sources, routing queries to the appropriate source by predicate.
Collections implement ReadableData/MaterializedData interfaces, so they
work as drop-in replacements for FactBase in evaluators.
"""
from prototyping_inference_engine.api.data.collection.protocols import (
    Queryable,
    Materializable,
    DynamicPredicates,
)
from prototyping_inference_engine.api.data.collection.readable_collection import (
    ReadableDataCollection,
)
from prototyping_inference_engine.api.data.collection.materialized_collection import (
    MaterializedDataCollection,
)
from prototyping_inference_engine.api.data.collection.writable_collection import (
    WritableDataCollection,
)
from prototyping_inference_engine.api.data.collection.builder import (
    ReadableCollectionBuilder,
    MaterializedCollectionBuilder,
    WritableCollectionBuilder,
)

__all__ = [
    "Queryable",
    "Materializable",
    "DynamicPredicates",
    "ReadableDataCollection",
    "MaterializedDataCollection",
    "WritableDataCollection",
    "ReadableCollectionBuilder",
    "MaterializedCollectionBuilder",
    "WritableCollectionBuilder",
]
