"""
Factory for creating Constant instances.

This factory delegates storage to a TermStorageStrategy,
enabling different caching behaviors (dict, weak references, etc.).
"""

from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.storage.storage_strategy import (
        TermStorageStrategy,
    )
    from prototyping_inference_engine.api.atom.term.constant import Constant


class ConstantFactory:
    """
    Factory for creating and tracking Constant instances.

    Uses a storage strategy to determine caching behavior.
    """

    def __init__(self, storage: "TermStorageStrategy[object, Constant]") -> None:
        """
        Initialize the factory with a storage strategy.

        Args:
            storage: The storage strategy for caching constants
        """
        self._storage = storage

    def create(self, identifier: object) -> "Constant":
        """
        Create or get a constant by identifier.

        If a constant with this identifier already exists in storage,
        returns the existing instance. Otherwise creates a new one.

        Args:
            identifier: The constant identifier (e.g., "a", 42, etc.)

        Returns:
            The Constant instance
        """
        from prototyping_inference_engine.api.atom.term.constant import Constant

        return self._storage.get_or_create(identifier, lambda: Constant(identifier))

    @property
    def tracked(self) -> Set["Constant"]:
        """
        Return all constants created through this factory.

        Returns:
            A set of all tracked Constant instances
        """
        return self._storage.tracked_items()

    def __len__(self) -> int:
        """Return the number of tracked constants."""
        return len(self._storage)
