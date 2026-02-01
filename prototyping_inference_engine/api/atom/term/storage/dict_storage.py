"""
Simple dictionary-based storage strategy.

This storage keeps all items in memory until explicitly cleared.
No automatic cleanup occurs.
"""
from typing import TypeVar, Generic, Callable, Set, Optional

K = TypeVar('K')
V = TypeVar('V')


class DictStorage(Generic[K, V]):
    """
    Storage strategy using a simple dictionary.

    Items are retained indefinitely until clear() is called.
    Use this when you want full control over cleanup timing.
    """

    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def get_or_create(self, key: K, creator: Callable[[], V]) -> V:
        """
        Get an existing value or create a new one.

        Args:
            key: The key to look up
            creator: A callable that creates the value if not found

        Returns:
            The existing or newly created value
        """
        if key not in self._data:
            self._data[key] = creator()
        return self._data[key]

    def get(self, key: K) -> Optional[V]:
        """
        Get a value by key, or None if not found.

        Args:
            key: The key to look up

        Returns:
            The value if found, None otherwise
        """
        return self._data.get(key)

    def contains(self, key: K) -> bool:
        """
        Check if a key exists in storage.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        return key in self._data

    def tracked_items(self) -> Set[V]:
        """
        Return all currently tracked values.

        Returns:
            A set of all values currently in storage
        """
        return set(self._data.values())

    def clear(self) -> int:
        """
        Clear all stored values.

        Returns:
            The number of items that were cleared
        """
        count = len(self._data)
        self._data.clear()
        return count

    def __len__(self) -> int:
        """Return the number of items in storage."""
        return len(self._data)
