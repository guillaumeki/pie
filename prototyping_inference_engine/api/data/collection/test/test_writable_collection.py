"""Tests for WritableDataCollection."""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.data.collection.writable_collection import (
    WritableDataCollection,
)
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestWritableDataCollection(unittest.TestCase):
    """Test WritableDataCollection."""

    def setUp(self):
        self.parser = DlgpeParser.instance()
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.r = Predicate("r", 1)

    def test_add_to_mapped_writable_source(self):
        """Test adding atom to a mapped writable source."""
        fb = MutableInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        collection = WritableDataCollection({self.p: fb})

        atom = Atom(self.p, Constant("c"), Constant("d"))
        collection.add(atom)

        self.assertIn(atom, collection)
        self.assertIn(atom, fb)
        self.assertEqual(len(fb), 2)

    def test_add_to_default_writable(self):
        """Test adding atom with unmapped predicate to default writable."""
        fb_p = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        fb_default = MutableInMemoryFactBase()

        collection = WritableDataCollection(
            sources={self.p: fb_p},
            default_writable=fb_default,
        )

        # Add atom with predicate not in sources
        atom = Atom(self.q, Constant("x"))
        collection.add(atom)

        self.assertIn(atom, collection)
        self.assertIn(atom, fb_default)

        # Predicate should now be mapped
        self.assertTrue(collection.has_predicate(self.q))
        self.assertIs(collection.get_source_for_predicate(self.q), fb_default)

    def test_add_no_source_no_default_raises(self):
        """Test adding atom without source or default raises KeyError."""
        fb_p = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        collection = WritableDataCollection(
            sources={self.p: fb_p},
            default_writable=None,
        )

        atom = Atom(self.q, Constant("x"))
        with self.assertRaises(KeyError):
            collection.add(atom)

    def test_add_non_writable_source_raises(self):
        """Test adding to non-writable source raises TypeError."""
        fb_frozen = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        collection = WritableDataCollection({self.p: fb_frozen})

        atom = Atom(self.p, Constant("c"), Constant("d"))
        with self.assertRaises(TypeError):
            collection.add(atom)

    def test_update_multiple_atoms(self):
        """Test update method adds multiple atoms."""
        fb = MutableInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        collection = WritableDataCollection({self.p: fb})

        atoms = [
            Atom(self.p, Constant("c"), Constant("d")),
            Atom(self.p, Constant("e"), Constant("f")),
        ]
        collection.update(atoms)

        self.assertEqual(len(fb), 3)
        for atom in atoms:
            self.assertIn(atom, collection)

    def test_update_to_multiple_sources(self):
        """Test update routes atoms to correct sources."""
        fb_p = MutableInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        fb_q = MutableInMemoryFactBase(self.parser.parse_atoms("q(x)."))

        collection = WritableDataCollection(
            {
                self.p: fb_p,
                self.q: fb_q,
            }
        )

        atoms = [
            Atom(self.p, Constant("c"), Constant("d")),
            Atom(self.q, Constant("y")),
        ]
        collection.update(atoms)

        self.assertEqual(len(fb_p), 2)
        self.assertEqual(len(fb_q), 2)

    def test_cache_invalidation_on_add(self):
        """Test that term caches are invalidated when adding atoms."""
        fb = MutableInMemoryFactBase(self.parser.parse_atoms("p(a,b)."))
        collection = WritableDataCollection({self.p: fb})

        # Access cached properties
        _ = collection.variables
        _ = collection.constants
        _ = collection.terms

        # Add new atom
        atom = Atom(self.p, Constant("c"), Constant("d"))
        collection.add(atom)

        # Constants should now include c and d
        self.assertIn(Constant("c"), collection.constants)
        self.assertIn(Constant("d"), collection.constants)

    def test_repr(self):
        """Test repr."""
        fb = MutableInMemoryFactBase()
        collection = WritableDataCollection({self.p: fb})
        r = repr(collection)
        self.assertIn("WritableDataCollection", r)

    def test_repr_with_default_writable(self):
        """Test repr shows writable when default_writable is set."""
        fb = MutableInMemoryFactBase()
        collection = WritableDataCollection({self.p: fb}, default_writable=fb)
        r = repr(collection)
        self.assertIn("WritableDataCollection", r)
        self.assertIn("writable", r)


class TestWritableCollectionWithDynamicSources(unittest.TestCase):
    """Test WritableDataCollection with dynamic sources."""

    def test_add_discovers_dynamic_source(self):
        """Test that adding atom discovers predicate from dynamic source."""
        parser = DlgpeParser.instance()
        p = Predicate("p", 2)
        q = Predicate("q", 1)

        fb_p = MutableInMemoryFactBase(parser.parse_atoms("p(a,b)."))
        fb_q = MutableInMemoryFactBase(parser.parse_atoms("q(x)."))

        collection = WritableDataCollection(
            sources={p: fb_p},
            dynamic_sources=[fb_q],
        )

        # q should be discoverable
        self.assertTrue(collection.has_predicate(q))

        # Add to q
        atom = Atom(q, Constant("y"))
        collection.add(atom)

        self.assertIn(atom, fb_q)


if __name__ == "__main__":
    unittest.main()
