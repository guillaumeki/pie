"""
Builder classes for constructing data collections with validation.
"""
from typing import Dict, List, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.data.collection.protocols import (
    Queryable,
    Materializable,
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
from prototyping_inference_engine.api.fact_base.protocols import Writable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.predicate import Predicate


class ReadableCollectionBuilder:
    """
    Fluent builder for constructing ReadableDataCollection instances.

    Example:
        collection = (ReadableCollectionBuilder()
            .add_all_predicates_from(fact_base_1)
            .add_predicate(person_pred, person_api)
            .add_dynamic_source(dynamic_db)
            .build())
    """

    def __init__(self):
        self._sources: Dict["Predicate", Queryable] = {}
        self._dynamic_sources: List[Queryable] = []

    def add_predicate(
        self,
        predicate: "Predicate",
        source: Queryable,
    ) -> "ReadableCollectionBuilder":
        """
        Map a single predicate to a source.

        Args:
            predicate: The predicate to map
            source: The data source for this predicate

        Returns:
            self for method chaining

        Raises:
            ValueError: If the predicate is already mapped to a different source
        """
        if predicate in self._sources and self._sources[predicate] is not source:
            raise ValueError(
                f"Predicate {predicate} is already mapped to a different source"
            )
        self._sources[predicate] = source
        return self

    def add_all_predicates_from(self, source: Queryable) -> "ReadableCollectionBuilder":
        """
        Add all predicates from a source.

        Args:
            source: The data source to add predicates from

        Returns:
            self for method chaining

        Raises:
            ValueError: If any predicate is already mapped to a different source
        """
        for predicate in source.get_predicates():
            if predicate in self._sources and self._sources[predicate] is not source:
                raise ValueError(
                    f"Predicate {predicate} is already mapped to a different source"
                )
            self._sources[predicate] = source
        return self

    def add_dynamic_source(self, source: Queryable) -> "ReadableCollectionBuilder":
        """
        Add a source that may provide predicates dynamically.

        Dynamic sources are checked when a predicate is not found in the
        static mapping.

        Args:
            source: The dynamic data source

        Returns:
            self for method chaining
        """
        if source not in self._dynamic_sources:
            self._dynamic_sources.append(source)
        return self

    def build(self) -> ReadableDataCollection:
        """
        Build the ReadableDataCollection.

        Returns:
            A new ReadableDataCollection with the configured sources
        """
        return ReadableDataCollection(
            sources=dict(self._sources),
            dynamic_sources=list(self._dynamic_sources) if self._dynamic_sources else None,
        )


class MaterializedCollectionBuilder:
    """
    Fluent builder for constructing MaterializedDataCollection instances.

    All sources must implement Materializable.

    Example:
        collection = (MaterializedCollectionBuilder()
            .add_all_predicates_from(in_memory_db_1)
            .add_all_predicates_from(in_memory_db_2)
            .build())
    """

    def __init__(self):
        self._sources: Dict["Predicate", Queryable] = {}
        self._dynamic_sources: List[Queryable] = []

    def _validate_materializable(self, source: Queryable) -> None:
        """Validate that a source implements Materializable."""
        if not isinstance(source, Materializable):
            raise TypeError(
                f"Source must implement Materializable, "
                f"but {type(source).__name__} does not"
            )

    def add_predicate(
        self,
        predicate: "Predicate",
        source: Queryable,
    ) -> "MaterializedCollectionBuilder":
        """
        Map a single predicate to a materialized source.

        Args:
            predicate: The predicate to map
            source: The data source for this predicate (must be Materializable)

        Returns:
            self for method chaining

        Raises:
            ValueError: If the predicate is already mapped to a different source
            TypeError: If the source does not implement Materializable
        """
        self._validate_materializable(source)
        if predicate in self._sources and self._sources[predicate] is not source:
            raise ValueError(
                f"Predicate {predicate} is already mapped to a different source"
            )
        self._sources[predicate] = source
        return self

    def add_all_predicates_from(
        self,
        source: Queryable,
    ) -> "MaterializedCollectionBuilder":
        """
        Add all predicates from a materialized source.

        Args:
            source: The data source to add predicates from (must be Materializable)

        Returns:
            self for method chaining

        Raises:
            ValueError: If any predicate is already mapped to a different source
            TypeError: If the source does not implement Materializable
        """
        self._validate_materializable(source)
        for predicate in source.get_predicates():
            if predicate in self._sources and self._sources[predicate] is not source:
                raise ValueError(
                    f"Predicate {predicate} is already mapped to a different source"
                )
            self._sources[predicate] = source
        return self

    def add_dynamic_source(self, source: Queryable) -> "MaterializedCollectionBuilder":
        """
        Add a materialized source that may provide predicates dynamically.

        Args:
            source: The dynamic data source (must be Materializable)

        Returns:
            self for method chaining

        Raises:
            TypeError: If the source does not implement Materializable
        """
        self._validate_materializable(source)
        if source not in self._dynamic_sources:
            self._dynamic_sources.append(source)
        return self

    def build(self) -> MaterializedDataCollection:
        """
        Build the MaterializedDataCollection.

        Returns:
            A new MaterializedDataCollection with the configured sources
        """
        return MaterializedDataCollection(
            sources=dict(self._sources),
            dynamic_sources=list(self._dynamic_sources) if self._dynamic_sources else None,
        )


class WritableCollectionBuilder:
    """
    Fluent builder for constructing WritableDataCollection instances.

    All sources must implement Materializable. Sources for writing must
    also implement Writable.

    Example:
        collection = (WritableCollectionBuilder()
            .add_all_predicates_from(read_only_db)
            .set_default_writable(writable_db)
            .build())
    """

    def __init__(self):
        self._sources: Dict["Predicate", Queryable] = {}
        self._dynamic_sources: List[Queryable] = []
        self._default_writable: Optional[Writable] = None

    def _validate_materializable(self, source: Queryable) -> None:
        """Validate that a source implements Materializable."""
        if not isinstance(source, Materializable):
            raise TypeError(
                f"Source must implement Materializable, "
                f"but {type(source).__name__} does not"
            )

    def add_predicate(
        self,
        predicate: "Predicate",
        source: Queryable,
    ) -> "WritableCollectionBuilder":
        """
        Map a single predicate to a materialized source.

        Args:
            predicate: The predicate to map
            source: The data source for this predicate (must be Materializable)

        Returns:
            self for method chaining

        Raises:
            ValueError: If the predicate is already mapped to a different source
            TypeError: If the source does not implement Materializable
        """
        self._validate_materializable(source)
        if predicate in self._sources and self._sources[predicate] is not source:
            raise ValueError(
                f"Predicate {predicate} is already mapped to a different source"
            )
        self._sources[predicate] = source
        return self

    def add_all_predicates_from(self, source: Queryable) -> "WritableCollectionBuilder":
        """
        Add all predicates from a materialized source.

        Args:
            source: The data source to add predicates from (must be Materializable)

        Returns:
            self for method chaining

        Raises:
            ValueError: If any predicate is already mapped to a different source
            TypeError: If the source does not implement Materializable
        """
        self._validate_materializable(source)
        for predicate in source.get_predicates():
            if predicate in self._sources and self._sources[predicate] is not source:
                raise ValueError(
                    f"Predicate {predicate} is already mapped to a different source"
                )
            self._sources[predicate] = source
        return self

    def add_dynamic_source(self, source: Queryable) -> "WritableCollectionBuilder":
        """
        Add a materialized source that may provide predicates dynamically.

        Args:
            source: The dynamic data source (must be Materializable)

        Returns:
            self for method chaining

        Raises:
            TypeError: If the source does not implement Materializable
        """
        self._validate_materializable(source)
        if source not in self._dynamic_sources:
            self._dynamic_sources.append(source)
        return self

    def set_default_writable(self, source: Writable) -> "WritableCollectionBuilder":
        """
        Set the default destination for atoms with unmapped predicates.

        Args:
            source: The default writable source (must be Materializable and Writable)

        Returns:
            self for method chaining

        Raises:
            TypeError: If the source does not implement Materializable
        """
        self._validate_materializable(source)
        self._default_writable = source
        return self

    def build(self) -> WritableDataCollection:
        """
        Build the WritableDataCollection.

        Returns:
            A new WritableDataCollection with the configured sources
        """
        return WritableDataCollection(
            sources=dict(self._sources),
            dynamic_sources=list(self._dynamic_sources) if self._dynamic_sources else None,
            default_writable=self._default_writable,
        )
