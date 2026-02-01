"""
Weak reference-based storage strategy.

This storage uses WeakValueDictionary to allow automatic garbage
collection of items that are no longer referenced elsewhere.
"""
from typing import TypeVar, Generic, Callable, Set, Optional
from weakref import WeakValueDictionary

K = TypeVar('K')
V = TypeVar('V')


class WeakRefStorage(Generic[K, V]):
    """
    Storage strategy using weak references.

    Items are automatically removed when no longer referenced
    by any other object (atoms, queries, rules, etc.).
    Use this for automatic memory management in sessions.

    Note: Values must be weak-referenceable (most objects are,
    but built-in types like str, int are not).
    """

    def __init__(self) -> None:
        self._data: WeakValueDictionary[K, V] = WeakValueDictionary()

    def get_or_create(self, key: K, creator: Callable[[], V]) -> V:
        """
        Get an existing value or create a new one.

        Args:
            key: The key to look up
            creator: A callable that creates the value if not found

        Returns:
            The existing or newly created value
        """
        value = self._data.get(key)
        if value is None:
            value = creator()
            self._data[key] = value
        return value

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

        Note: This creates strong references to all values,
        preventing their garbage collection while the set exists.

        Returns:
            A set of all values currently in storage
        """
        return set(self._data.values())

    def clear(self) -> int:
        """
        Clear all stored values.

        Note: This only removes entries from the WeakValueDictionary.
        The actual objects may still exist if referenced elsewhere.

        Returns:
            The number of items that were cleared
        """
        count = len(self._data)
        self._data.clear()
        return count

    def __len__(self) -> int:
        """Return the number of items in storage."""
        return len(self._data)
