"""
Factory for creating Predicate instances.

This factory delegates storage to a TermStorageStrategy,
enabling different caching behaviors (dict, weak references, etc.).
"""

from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.storage.storage_strategy import (
        TermStorageStrategy,
    )
    from prototyping_inference_engine.api.atom.predicate import Predicate


class PredicateFactory:
    """
    Factory for creating and tracking Predicate instances.

    Uses a storage strategy to determine caching behavior.
    Predicates are keyed by (name, arity) tuples.
    """

    def __init__(
        self, storage: "TermStorageStrategy[tuple[str, int], Predicate]"
    ) -> None:
        """
        Initialize the factory with a storage strategy.

        Args:
            storage: The storage strategy for caching predicates
        """
        self._storage = storage

    def create(self, name: str, arity: int) -> "Predicate":
        """
        Create or get a predicate by name and arity.

        If a predicate with this (name, arity) already exists in storage,
        returns the existing instance. Otherwise creates a new one.

        Args:
            name: The predicate name (e.g., "p", "parent")
            arity: The number of arguments (e.g., 2 for binary predicates)

        Returns:
            The Predicate instance
        """
        from prototyping_inference_engine.api.atom.predicate import Predicate

        return self._storage.get_or_create(
            (name, arity), lambda: Predicate(name, arity)
        )

    @property
    def tracked(self) -> Set["Predicate"]:
        """
        Return all predicates created through this factory.

        Returns:
            A set of all tracked Predicate instances
        """
        return self._storage.tracked_items()

    def __len__(self) -> int:
        """Return the number of tracked predicates."""
        return len(self._storage)
