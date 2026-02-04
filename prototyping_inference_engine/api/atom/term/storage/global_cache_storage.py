"""
Global cache delegation storage strategy.

This storage delegates to the existing global caches (Variable.variables,
Constant's @cache, etc.) for backward compatibility with non-session code.
"""

from typing import TypeVar, Generic, Callable, Set, Optional

K = TypeVar("K")
V = TypeVar("V")


class GlobalCacheStorage(Generic[K, V]):
    """
    Storage strategy that delegates to a global cache.

    This adapter wraps an existing global cache (like Variable.variables)
    to make it compatible with the TermStorageStrategy protocol.
    Use this for backward compatibility when you want session code
    to share the same cache as non-session code.

    Note: clear() on this storage will NOT clear the global cache,
    as that could affect other parts of the application.
    """

    def __init__(self, global_cache: dict[K, V]) -> None:
        """
        Initialize with a reference to a global cache.

        Args:
            global_cache: The global dictionary to delegate to
        """
        self._global_cache = global_cache
        self._tracked_keys: set[K] = set()

    def get_or_create(self, key: K, creator: Callable[[], V]) -> V:
        """
        Get an existing value or create a new one.

        The value is stored in the global cache.

        Args:
            key: The key to look up
            creator: A callable that creates the value if not found

        Returns:
            The existing or newly created value
        """
        if key not in self._global_cache:
            self._global_cache[key] = creator()
        self._tracked_keys.add(key)
        return self._global_cache[key]

    def get(self, key: K) -> Optional[V]:
        """
        Get a value by key, or None if not found.

        Args:
            key: The key to look up

        Returns:
            The value if found, None otherwise
        """
        return self._global_cache.get(key)

    def contains(self, key: K) -> bool:
        """
        Check if a key exists in the global cache.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        return key in self._global_cache

    def tracked_items(self) -> Set[V]:
        """
        Return values that were accessed through this storage.

        Only returns items that were get_or_create'd through
        this storage instance, not all items in the global cache.

        Returns:
            A set of values accessed through this storage
        """
        return {
            self._global_cache[k] for k in self._tracked_keys if k in self._global_cache
        }

    def clear(self) -> int:
        """
        Clear tracking, but NOT the global cache.

        This only forgets which keys were tracked by this storage.
        The global cache remains untouched to avoid side effects.

        Returns:
            The number of tracked keys that were cleared
        """
        count = len(self._tracked_keys)
        self._tracked_keys.clear()
        return count

    def __len__(self) -> int:
        """Return the number of tracked items (not the global cache size)."""
        return len(self._tracked_keys)
