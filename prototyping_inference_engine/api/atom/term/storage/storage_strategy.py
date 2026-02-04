"""
Storage strategy protocol for term caching.

This module defines the interface for term storage strategies,
enabling different caching behaviors (dict, weak references, etc.)
to be injected into term factories.
"""

from typing import Protocol, TypeVar, Callable, Set, Optional, runtime_checkable

K = TypeVar("K", contravariant=True)
V = TypeVar("V")


@runtime_checkable
class TermStorageStrategy(Protocol[K, V]):
    """
    Protocol for term storage strategies.

    A storage strategy determines how terms are cached and when they
    can be garbage collected. Different implementations support:
    - Simple dict storage (no auto-cleanup)
    - Weak reference storage (auto-cleanup when unreferenced)
    - Global cache delegation (backward compatibility)
    """

    def get_or_create(self, key: K, creator: Callable[[], V]) -> V:
        """
        Get an existing value or create a new one.

        Args:
            key: The key to look up
            creator: A callable that creates the value if not found

        Returns:
            The existing or newly created value
        """
        ...

    def get(self, key: K) -> Optional[V]:
        """
        Get a value by key, or None if not found.

        Args:
            key: The key to look up

        Returns:
            The value if found, None otherwise
        """
        ...

    def contains(self, key: K) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        ...

    def tracked_items(self) -> Set[V]:
        """
        Return all currently tracked values.

        Returns:
            A set of all values currently in storage
        """
        ...

    def clear(self) -> int:
        """
        Clear all stored values.

        Returns:
            The number of items that were cleared
        """
        ...

    def __len__(self) -> int:
        """Return the number of items in storage."""
        ...
