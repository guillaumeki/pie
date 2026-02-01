"""
Unit tests for term storage strategies.
"""
import gc
import unittest
from typing import runtime_checkable
from unittest import TestCase

from prototyping_inference_engine.api.atom.term.storage import (
    TermStorageStrategy,
    DictStorage,
    WeakRefStorage,
    GlobalCacheStorage,
)


class DummyObject:
    """A simple object for testing weak references."""

    def __init__(self, value: str):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, DummyObject):
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)


class TestDictStorage(TestCase):
    """Tests for DictStorage."""

    def test_get_or_create_creates_new_item(self):
        """Test that get_or_create creates a new item when key doesn't exist."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        obj = storage.get_or_create("key1", lambda: DummyObject("value1"))
        self.assertEqual(obj.value, "value1")
        self.assertEqual(len(storage), 1)

    def test_get_or_create_returns_existing_item(self):
        """Test that get_or_create returns existing item without calling creator."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        obj1 = storage.get_or_create("key1", lambda: DummyObject("value1"))
        obj2 = storage.get_or_create("key1", lambda: DummyObject("different"))
        self.assertIs(obj1, obj2)
        self.assertEqual(obj2.value, "value1")

    def test_get_returns_existing_item(self):
        """Test that get returns an existing item."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        storage.get_or_create("key1", lambda: DummyObject("value1"))
        obj = storage.get("key1")
        self.assertIsNotNone(obj)
        self.assertEqual(obj.value, "value1")

    def test_get_returns_none_for_missing_key(self):
        """Test that get returns None for missing key."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        obj = storage.get("nonexistent")
        self.assertIsNone(obj)

    def test_contains_true_for_existing_key(self):
        """Test that contains returns True for existing key."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        storage.get_or_create("key1", lambda: DummyObject("value1"))
        self.assertTrue(storage.contains("key1"))

    def test_contains_false_for_missing_key(self):
        """Test that contains returns False for missing key."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        self.assertFalse(storage.contains("nonexistent"))

    def test_tracked_items_returns_all_values(self):
        """Test that tracked_items returns all stored values."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        obj1 = storage.get_or_create("key1", lambda: DummyObject("value1"))
        obj2 = storage.get_or_create("key2", lambda: DummyObject("value2"))
        tracked = storage.tracked_items()
        self.assertEqual(tracked, {obj1, obj2})

    def test_clear_removes_all_items(self):
        """Test that clear removes all items and returns count."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        storage.get_or_create("key1", lambda: DummyObject("value1"))
        storage.get_or_create("key2", lambda: DummyObject("value2"))
        count = storage.clear()
        self.assertEqual(count, 2)
        self.assertEqual(len(storage), 0)
        self.assertIsNone(storage.get("key1"))

    def test_len_returns_item_count(self):
        """Test that len returns the number of items."""
        storage: DictStorage[str, DummyObject] = DictStorage()
        self.assertEqual(len(storage), 0)
        storage.get_or_create("key1", lambda: DummyObject("value1"))
        self.assertEqual(len(storage), 1)
        storage.get_or_create("key2", lambda: DummyObject("value2"))
        self.assertEqual(len(storage), 2)


class TestWeakRefStorage(TestCase):
    """Tests for WeakRefStorage."""

    def test_get_or_create_creates_new_item(self):
        """Test that get_or_create creates a new item when key doesn't exist."""
        storage: WeakRefStorage[str, DummyObject] = WeakRefStorage()
        obj = storage.get_or_create("key1", lambda: DummyObject("value1"))
        self.assertEqual(obj.value, "value1")
        self.assertEqual(len(storage), 1)

    def test_get_or_create_returns_existing_item(self):
        """Test that get_or_create returns existing item without calling creator."""
        storage: WeakRefStorage[str, DummyObject] = WeakRefStorage()
        obj1 = storage.get_or_create("key1", lambda: DummyObject("value1"))
        obj2 = storage.get_or_create("key1", lambda: DummyObject("different"))
        self.assertIs(obj1, obj2)

    def test_item_removed_when_unreferenced(self):
        """Test that items are removed when no longer referenced."""
        storage: WeakRefStorage[str, DummyObject] = WeakRefStorage()

        def create_and_forget():
            obj = storage.get_or_create("temp", lambda: DummyObject("temporary"))
            return None  # Don't return the reference

        create_and_forget()
        gc.collect()
        self.assertIsNone(storage.get("temp"))
        self.assertEqual(len(storage), 0)

    def test_item_retained_when_referenced(self):
        """Test that items are retained when still referenced."""
        storage: WeakRefStorage[str, DummyObject] = WeakRefStorage()
        obj = storage.get_or_create("key1", lambda: DummyObject("value1"))
        gc.collect()
        self.assertEqual(len(storage), 1)
        retrieved = storage.get("key1")
        self.assertIs(retrieved, obj)

    def test_get_returns_none_for_missing_key(self):
        """Test that get returns None for missing key."""
        storage: WeakRefStorage[str, DummyObject] = WeakRefStorage()
        self.assertIsNone(storage.get("nonexistent"))

    def test_contains_false_after_gc(self):
        """Test that contains returns False after item is garbage collected."""
        storage: WeakRefStorage[str, DummyObject] = WeakRefStorage()

        def create_and_forget():
            storage.get_or_create("temp", lambda: DummyObject("temporary"))

        create_and_forget()
        gc.collect()
        self.assertFalse(storage.contains("temp"))

    def test_tracked_items_returns_live_values(self):
        """Test that tracked_items returns only live values."""
        storage: WeakRefStorage[str, DummyObject] = WeakRefStorage()
        obj1 = storage.get_or_create("key1", lambda: DummyObject("value1"))

        def create_and_forget():
            storage.get_or_create("temp", lambda: DummyObject("temporary"))

        create_and_forget()
        gc.collect()
        tracked = storage.tracked_items()
        self.assertEqual(tracked, {obj1})

    def test_clear_removes_entries(self):
        """Test that clear removes all entries."""
        storage: WeakRefStorage[str, DummyObject] = WeakRefStorage()
        obj = storage.get_or_create("key1", lambda: DummyObject("value1"))
        count = storage.clear()
        self.assertEqual(count, 1)
        self.assertEqual(len(storage), 0)
        # Object still exists because we hold a reference
        self.assertIsNotNone(obj)


class TestGlobalCacheStorage(TestCase):
    """Tests for GlobalCacheStorage."""

    def setUp(self):
        """Set up a fresh global cache for each test."""
        self.global_cache: dict[str, DummyObject] = {}

    def test_get_or_create_adds_to_global_cache(self):
        """Test that get_or_create adds items to the global cache."""
        storage: GlobalCacheStorage[str, DummyObject] = GlobalCacheStorage(
            self.global_cache
        )
        obj = storage.get_or_create("key1", lambda: DummyObject("value1"))
        self.assertEqual(obj.value, "value1")
        self.assertIn("key1", self.global_cache)
        self.assertIs(self.global_cache["key1"], obj)

    def test_get_or_create_returns_existing_from_global(self):
        """Test that get_or_create returns existing item from global cache."""
        self.global_cache["key1"] = DummyObject("preexisting")
        storage: GlobalCacheStorage[str, DummyObject] = GlobalCacheStorage(
            self.global_cache
        )
        obj = storage.get_or_create("key1", lambda: DummyObject("new"))
        self.assertEqual(obj.value, "preexisting")

    def test_get_returns_from_global_cache(self):
        """Test that get returns items from global cache."""
        self.global_cache["key1"] = DummyObject("value1")
        storage: GlobalCacheStorage[str, DummyObject] = GlobalCacheStorage(
            self.global_cache
        )
        obj = storage.get("key1")
        self.assertIsNotNone(obj)
        self.assertEqual(obj.value, "value1")

    def test_contains_checks_global_cache(self):
        """Test that contains checks the global cache."""
        self.global_cache["key1"] = DummyObject("value1")
        storage: GlobalCacheStorage[str, DummyObject] = GlobalCacheStorage(
            self.global_cache
        )
        self.assertTrue(storage.contains("key1"))
        self.assertFalse(storage.contains("nonexistent"))

    def test_tracked_items_returns_only_accessed_items(self):
        """Test that tracked_items returns only items accessed via this storage."""
        self.global_cache["preexisting"] = DummyObject("old")
        storage: GlobalCacheStorage[str, DummyObject] = GlobalCacheStorage(
            self.global_cache
        )
        obj = storage.get_or_create("new", lambda: DummyObject("new"))
        tracked = storage.tracked_items()
        self.assertEqual(tracked, {obj})
        self.assertNotIn(self.global_cache["preexisting"], tracked)

    def test_clear_does_not_affect_global_cache(self):
        """Test that clear does not remove items from global cache."""
        storage: GlobalCacheStorage[str, DummyObject] = GlobalCacheStorage(
            self.global_cache
        )
        storage.get_or_create("key1", lambda: DummyObject("value1"))
        storage.clear()
        # Global cache still has the item
        self.assertIn("key1", self.global_cache)
        # But tracked items is now empty
        self.assertEqual(storage.tracked_items(), set())

    def test_len_returns_tracked_count_not_global(self):
        """Test that len returns tracked count, not global cache size."""
        self.global_cache["preexisting"] = DummyObject("old")
        storage: GlobalCacheStorage[str, DummyObject] = GlobalCacheStorage(
            self.global_cache
        )
        self.assertEqual(len(storage), 0)
        storage.get_or_create("new", lambda: DummyObject("new"))
        self.assertEqual(len(storage), 1)
        # Global cache has 2, but we only tracked 1
        self.assertEqual(len(self.global_cache), 2)


class TestProtocolCompliance(TestCase):
    """Tests to verify protocol compliance."""

    def test_dict_storage_is_runtime_checkable(self):
        """Test that DictStorage satisfies TermStorageStrategy protocol."""
        storage = DictStorage()
        self.assertIsInstance(storage, TermStorageStrategy)

    def test_weak_ref_storage_is_runtime_checkable(self):
        """Test that WeakRefStorage satisfies TermStorageStrategy protocol."""
        storage = WeakRefStorage()
        self.assertIsInstance(storage, TermStorageStrategy)

    def test_global_cache_storage_is_runtime_checkable(self):
        """Test that GlobalCacheStorage satisfies TermStorageStrategy protocol."""
        storage = GlobalCacheStorage({})
        self.assertIsInstance(storage, TermStorageStrategy)


if __name__ == "__main__":
    unittest.main()
