"""Tests for collection builders."""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.data.collection.builder import (
    ReadableCollectionBuilder,
    MaterializedCollectionBuilder,
    WritableCollectionBuilder,
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
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.io.parsers.dlgp.dlgp2_parser import Dlgp2Parser


class TestReadableCollectionBuilder(unittest.TestCase):
    """Test ReadableCollectionBuilder."""

    def setUp(self):
        self.parser = Dlgp2Parser.instance()
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.fb1 = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        self.fb2 = FrozenInMemoryFactBase(self.parser.parse_atoms("q(x)."))

    def test_build_empty(self):
        """Test building empty collection."""
        collection = ReadableCollectionBuilder().build()
        self.assertIsInstance(collection, ReadableDataCollection)
        self.assertEqual(list(collection.get_predicates()), [])

    def test_add_predicate(self):
        """Test add_predicate method."""
        collection = ReadableCollectionBuilder().add_predicate(self.p, self.fb1).build()
        self.assertTrue(collection.has_predicate(self.p))
        self.assertFalse(collection.has_predicate(self.q))

    def test_add_predicate_duplicate_same_source(self):
        """Test add_predicate with same source is allowed."""
        collection = (
            ReadableCollectionBuilder()
            .add_predicate(self.p, self.fb1)
            .add_predicate(self.p, self.fb1)  # Same source, allowed
            .build()
        )
        self.assertTrue(collection.has_predicate(self.p))

    def test_add_predicate_duplicate_different_source_raises(self):
        """Test add_predicate with different source raises ValueError."""
        builder = ReadableCollectionBuilder().add_predicate(self.p, self.fb1)
        with self.assertRaises(ValueError):
            builder.add_predicate(self.p, self.fb2)  # Different source

    def test_add_all_predicates_from(self):
        """Test add_all_predicates_from method."""
        collection = (
            ReadableCollectionBuilder()
            .add_all_predicates_from(self.fb1)
            .add_all_predicates_from(self.fb2)
            .build()
        )
        self.assertTrue(collection.has_predicate(self.p))
        self.assertTrue(collection.has_predicate(self.q))

    def test_add_all_predicates_from_conflict_raises(self):
        """Test add_all_predicates_from raises on predicate conflict."""
        # Both sources have predicate p
        fb_with_p = FrozenInMemoryFactBase(self.parser.parse_atoms("p(c,d)."))
        builder = ReadableCollectionBuilder().add_all_predicates_from(self.fb1)
        with self.assertRaises(ValueError):
            builder.add_all_predicates_from(fb_with_p)

    def test_add_dynamic_source(self):
        """Test add_dynamic_source method."""
        collection = (
            ReadableCollectionBuilder()
            .add_predicate(self.p, self.fb1)
            .add_dynamic_source(self.fb2)
            .build()
        )
        # q should be discoverable from dynamic source
        self.assertTrue(collection.has_predicate(self.q))

    def test_fluent_api(self):
        """Test fluent API returns builder for chaining."""
        builder = ReadableCollectionBuilder()
        result = builder.add_predicate(self.p, self.fb1)
        self.assertIs(result, builder)

        result = builder.add_all_predicates_from(self.fb2)
        self.assertIs(result, builder)

        result = builder.add_dynamic_source(self.fb1)
        self.assertIs(result, builder)


class TestMaterializedCollectionBuilder(unittest.TestCase):
    """Test MaterializedCollectionBuilder."""

    def setUp(self):
        self.parser = Dlgp2Parser.instance()
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.fb1 = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        self.fb2 = FrozenInMemoryFactBase(self.parser.parse_atoms("q(x)."))

    def test_build_returns_materialized_collection(self):
        """Test build returns MaterializedDataCollection."""
        collection = (
            MaterializedCollectionBuilder().add_all_predicates_from(self.fb1).build()
        )
        self.assertIsInstance(collection, MaterializedDataCollection)

    def test_add_predicate(self):
        """Test add_predicate method."""
        collection = (
            MaterializedCollectionBuilder().add_predicate(self.p, self.fb1).build()
        )
        self.assertTrue(collection.has_predicate(self.p))
        self.assertEqual(len(collection), 1)

    def test_add_all_predicates_from(self):
        """Test add_all_predicates_from method."""
        collection = (
            MaterializedCollectionBuilder()
            .add_all_predicates_from(self.fb1)
            .add_all_predicates_from(self.fb2)
            .build()
        )
        self.assertEqual(len(collection), 2)

    def test_add_dynamic_source(self):
        """Test add_dynamic_source method."""
        collection = (
            MaterializedCollectionBuilder()
            .add_predicate(self.p, self.fb1)
            .add_dynamic_source(self.fb2)
            .build()
        )
        self.assertTrue(collection.has_predicate(self.q))

    def test_non_materializable_raises(self):
        """Test non-Materializable source raises TypeError."""

        class NonMaterializableSource:
            def get_predicates(self):
                return iter([])

            def has_predicate(self, predicate):
                return False

            def get_atomic_pattern(self, predicate):
                raise KeyError()

            def evaluate(self, query):
                return iter([])

            def can_evaluate(self, query):
                return False

        source = NonMaterializableSource()
        with self.assertRaises(TypeError):
            MaterializedCollectionBuilder().add_predicate(self.p, source)

    def test_conflict_raises(self):
        """Test predicate conflict raises ValueError."""
        fb_with_p = FrozenInMemoryFactBase(self.parser.parse_atoms("p(c,d)."))
        builder = MaterializedCollectionBuilder().add_all_predicates_from(self.fb1)
        with self.assertRaises(ValueError):
            builder.add_all_predicates_from(fb_with_p)


class TestWritableCollectionBuilder(unittest.TestCase):
    """Test WritableCollectionBuilder."""

    def setUp(self):
        self.parser = Dlgp2Parser.instance()
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.fb_frozen = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        self.fb_mutable = MutableInMemoryFactBase(self.parser.parse_atoms("q(x)."))

    def test_build_returns_writable_collection(self):
        """Test build returns WritableDataCollection."""
        collection = (
            WritableCollectionBuilder().add_all_predicates_from(self.fb_frozen).build()
        )
        self.assertIsInstance(collection, WritableDataCollection)

    def test_add_predicate(self):
        """Test add_predicate method."""
        collection = (
            WritableCollectionBuilder().add_predicate(self.p, self.fb_frozen).build()
        )
        self.assertTrue(collection.has_predicate(self.p))

    def test_set_default_writable(self):
        """Test set_default_writable method."""
        collection = (
            WritableCollectionBuilder()
            .add_all_predicates_from(self.fb_frozen)
            .set_default_writable(self.fb_mutable)
            .build()
        )

        # Add atom with new predicate - should go to default writable
        r = Predicate("r", 1)
        atom = Atom(r, Constant("z"))
        collection.add(atom)

        self.assertIn(atom, collection)
        self.assertIn(atom, self.fb_mutable)

    def test_non_materializable_raises(self):
        """Test non-Materializable source raises TypeError."""

        class NonMaterializableSource:
            def get_predicates(self):
                return iter([])

            def has_predicate(self, predicate):
                return False

            def get_atomic_pattern(self, predicate):
                raise KeyError()

            def evaluate(self, query):
                return iter([])

            def can_evaluate(self, query):
                return False

        source = NonMaterializableSource()
        with self.assertRaises(TypeError):
            WritableCollectionBuilder().add_predicate(self.p, source)

    def test_fluent_api(self):
        """Test fluent API returns builder for chaining."""
        builder = WritableCollectionBuilder()
        result = builder.add_predicate(self.p, self.fb_frozen)
        self.assertIs(result, builder)

        result = builder.set_default_writable(self.fb_mutable)
        self.assertIs(result, builder)


class TestIntegration(unittest.TestCase):
    """Integration tests for collection builders."""

    def test_build_collection_from_multiple_fact_bases(self):
        """Test building a collection from multiple fact bases."""
        parser = Dlgp2Parser.instance()

        fb1 = FrozenInMemoryFactBase(parser.parse_atoms("person(alice), person(bob)."))
        fb2 = FrozenInMemoryFactBase(
            parser.parse_atoms("knows(alice, bob), knows(bob, carol).")
        )

        collection = (
            ReadableCollectionBuilder()
            .add_all_predicates_from(fb1)
            .add_all_predicates_from(fb2)
            .build()
        )

        person = Predicate("person", 1)
        knows = Predicate("knows", 2)

        self.assertTrue(collection.has_predicate(person))
        self.assertTrue(collection.has_predicate(knows))

    def test_writable_collection_routes_writes(self):
        """Test that writable collection routes writes to correct source."""
        parser = Dlgp2Parser.instance()
        p = Predicate("p", 1)
        q = Predicate("q", 1)

        fb_p = MutableInMemoryFactBase(parser.parse_atoms("p(a)."))
        fb_q = MutableInMemoryFactBase(parser.parse_atoms("q(x)."))

        collection = (
            WritableCollectionBuilder()
            .add_all_predicates_from(fb_p)
            .add_all_predicates_from(fb_q)
            .build()
        )

        # Add to p predicate
        atom_p = Atom(p, Constant("b"))
        collection.add(atom_p)
        self.assertIn(atom_p, fb_p)
        self.assertNotIn(atom_p, fb_q)

        # Add to q predicate
        atom_q = Atom(q, Constant("y"))
        collection.add(atom_q)
        self.assertIn(atom_q, fb_q)
        self.assertNotIn(atom_q, fb_p)


if __name__ == "__main__":
    unittest.main()
