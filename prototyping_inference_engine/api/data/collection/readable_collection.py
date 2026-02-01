"""
ReadableDataCollection for aggregating multiple queryable data sources.
"""
from typing import Dict, Iterator, List, Optional, Tuple, TYPE_CHECKING

from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.data.collection.protocols import (
    Queryable,
    DynamicPredicates,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.predicate import Predicate
    from prototyping_inference_engine.api.atom.term.term import Term
    from prototyping_inference_engine.api.data.atomic_pattern import AtomicPattern
    from prototyping_inference_engine.api.data.basic_query import BasicQuery


class ReadableDataCollection(ReadableData):
    """
    A collection that aggregates multiple queryable data sources.

    Each predicate is routed to exactly one source. Queries are delegated to
    the appropriate source based on the predicate.

    This class implements ReadableData, making it a drop-in replacement for
    FactBase in evaluators.

    Note: This implementation assumes single-threaded access. No synchronization
    is provided for concurrent access.
    """

    def __init__(
        self,
        sources: Dict["Predicate", Queryable],
        dynamic_sources: Optional[List[Queryable]] = None,
    ):
        """
        Create a collection from predicate-to-source mappings.

        Use ReadableCollectionBuilder for a more convenient construction API.

        Args:
            sources: Mapping from predicates to their data sources
            dynamic_sources: Sources that may add predicates dynamically.
                           These are checked when a predicate is not found
                           in the static mapping.
        """
        self._sources: Dict["Predicate", Queryable] = dict(sources)
        self._dynamic_sources: List[Queryable] = list(dynamic_sources) if dynamic_sources else []
        self._all_sources: List[Queryable] = list(set(sources.values()))
        if dynamic_sources:
            for ds in dynamic_sources:
                if ds not in self._all_sources:
                    self._all_sources.append(ds)

    def _refresh_dynamic_predicates(self) -> None:
        """Check dynamic sources for new predicates and update routing."""
        for source in self._dynamic_sources:
            if isinstance(source, DynamicPredicates):
                for predicate in source.get_predicates():
                    if predicate not in self._sources:
                        self._sources[predicate] = source

    def _get_source(self, predicate: "Predicate") -> Optional[Queryable]:
        """Get the source for a predicate, refreshing dynamic sources if needed."""
        if predicate in self._sources:
            return self._sources[predicate]

        # Check dynamic sources
        if self._dynamic_sources:
            self._refresh_dynamic_predicates()
            return self._sources.get(predicate)

        return None

    def get_predicates(self) -> Iterator["Predicate"]:
        """Return all predicates from all sources."""
        if self._dynamic_sources:
            self._refresh_dynamic_predicates()
        return iter(self._sources.keys())

    def has_predicate(self, predicate: "Predicate") -> bool:
        """Check if any source contains the given predicate."""
        return self._get_source(predicate) is not None

    def get_atomic_pattern(self, predicate: "Predicate") -> "AtomicPattern":
        """
        Get the atomic pattern for a predicate from its source.

        Args:
            predicate: The predicate to get the pattern for

        Returns:
            The atomic pattern from the source that owns this predicate

        Raises:
            KeyError: If no source contains this predicate
        """
        source = self._get_source(predicate)
        if source is None:
            raise KeyError(f"No source contains predicate: {predicate}")
        return source.get_atomic_pattern(predicate)

    def evaluate(self, query: "BasicQuery") -> Iterator[Tuple["Term", ...]]:
        """
        Evaluate a query by routing to the appropriate source.

        Args:
            query: The basic query to evaluate

        Returns:
            Iterator of term tuples from the source that owns the predicate

        Raises:
            KeyError: If no source contains the query's predicate
        """
        source = self._get_source(query.predicate)
        if source is None:
            raise KeyError(f"No source contains predicate: {query.predicate}")
        return source.evaluate(query)

    def can_evaluate(self, query: "BasicQuery") -> bool:
        """
        Check if the query can be evaluated by the appropriate source.

        Args:
            query: The basic query to check

        Returns:
            True if a source owns the predicate and can evaluate the query
        """
        source = self._get_source(query.predicate)
        if source is None:
            return False
        return source.can_evaluate(query)

    @property
    def sources(self) -> Dict["Predicate", Queryable]:
        """The predicate-to-source mapping (read-only view)."""
        if self._dynamic_sources:
            self._refresh_dynamic_predicates()
        return dict(self._sources)

    def get_source_for_predicate(self, predicate: "Predicate") -> Optional[Queryable]:
        """Get the source responsible for a predicate, or None if not found."""
        return self._get_source(predicate)

    def __repr__(self) -> str:
        predicates = list(self._sources.keys())
        if len(predicates) <= 3:
            pred_str = ", ".join(str(p) for p in predicates)
        else:
            pred_str = f"{len(predicates)} predicates"
        return f"ReadableDataCollection({pred_str})"
