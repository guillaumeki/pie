"""
Factory for creating Variable instances.

This factory delegates storage to a TermStorageStrategy,
enabling different caching behaviors (dict, weak references, etc.).
"""

from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.storage.storage_strategy import (
        TermStorageStrategy,
    )
    from prototyping_inference_engine.api.atom.term.variable import Variable


class VariableFactory:
    """
    Factory for creating and tracking Variable instances.

    Uses a storage strategy to determine caching behavior.
    Supports creation of named variables and fresh (unique) variables.
    """

    def __init__(self, storage: "TermStorageStrategy[str, Variable]") -> None:
        """
        Initialize the factory with a storage strategy.

        Args:
            storage: The storage strategy for caching variables
        """
        self._storage = storage
        self._fresh_counter = 0

    def create(self, identifier: str) -> "Variable":
        """
        Create or get a variable by identifier.

        If a variable with this identifier already exists in storage,
        returns the existing instance. Otherwise creates a new one.

        Args:
            identifier: The variable identifier (e.g., "X", "Y")

        Returns:
            The Variable instance
        """
        from prototyping_inference_engine.api.atom.term.variable import Variable

        return self._storage.get_or_create(identifier, lambda: Variable(identifier))

    def fresh(self) -> "Variable":
        """
        Create a fresh variable with a unique identifier.

        Fresh variables use the pattern _FV0, _FV1, _FV2, etc.
        The prefix _FV is chosen to avoid conflicts with user-defined
        variables and the global Variable.fresh_variable() which uses V0, V1, etc.

        Returns:
            A new Variable with a unique identifier
        """
        identifier = f"_FV{self._fresh_counter}"
        while self._storage.contains(identifier):
            self._fresh_counter += 1
            identifier = f"_FV{self._fresh_counter}"
        self._fresh_counter += 1
        return self.create(identifier)

    @property
    def tracked(self) -> Set["Variable"]:
        """
        Return all variables created through this factory.

        Returns:
            A set of all tracked Variable instances
        """
        return self._storage.tracked_items()

    def __len__(self) -> int:
        """Return the number of tracked variables."""
        return len(self._storage)
