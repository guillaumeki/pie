"""Tests for MaterializedDataCollection."""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.collection.materialized_collection import (
    MaterializedDataCollection,
)
from prototyping_inference_engine.api.data.materialized_data import MaterializedData
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestMaterializedDataCollection(unittest.TestCase):
    """Test MaterializedDataCollection."""

    def setUp(self):
        self.parser = Dlgp2Parser.instance()
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)

        self.fb1 = FrozenInMemoryFactBase(
            self.parser.parse_atoms("p(a,b), p(c,d).")
        )
        self.fb2 = FrozenInMemoryFactBase(
            self.parser.parse_atoms("q(x), q(y).")
        )

    def test_isinstance_materialized_data(self):
        """Test collection is instance of MaterializedData."""
        collection = MaterializedDataCollection({self.p: self.fb1})
        self.assertIsInstance(collection, MaterializedData)

    def test_iter_single_source(self):
        """Test iteration over single source."""
        collection = MaterializedDataCollection({self.p: self.fb1})
        atoms = set(collection)
        self.assertEqual(len(atoms), 2)

    def test_iter_multiple_sources(self):
        """Test iteration over multiple sources."""
        collection = MaterializedDataCollection({
            self.p: self.fb1,
            self.q: self.fb2,
        })
        atoms = set(collection)
        self.assertEqual(len(atoms), 4)

    def test_iter_no_duplicates(self):
        """Test iteration does not yield duplicates."""
        # Both sources share the same predicate
        fb1 = FrozenInMemoryFactBase(
            self.parser.parse_atoms("p(a,b).")
        )
        fb2 = FrozenInMemoryFactBase(
            self.parser.parse_atoms("p(a,b), p(c,d).")  # p(a,b) is duplicate
        )
        # Note: This setup maps different predicates, so no overlap
        # To test deduplication, we need the same atom in different sources
        # But our design is one predicate = one source, so this case shouldn't occur
        # Let's test with a dynamic source scenario
        collection = MaterializedDataCollection(
            sources={self.p: fb1},
            dynamic_sources=[fb2],
        )
        # The atoms from fb1 and fb2 might overlap if we didn't dedupe
        atoms = list(collection)
        # We should have unique atoms only
        self.assertEqual(len(atoms), len(set(atoms)))

    def test_len(self):
        """Test len returns total unique atom count."""
        collection = MaterializedDataCollection({
            self.p: self.fb1,
            self.q: self.fb2,
        })
        self.assertEqual(len(collection), 4)

    def test_contains(self):
        """Test containment check."""
        collection = MaterializedDataCollection({
            self.p: self.fb1,
            self.q: self.fb2,
        })
        atom_p = Atom(self.p, Constant("a"), Constant("b"))
        atom_q = Atom(self.q, Constant("x"))
        atom_r = Atom(Predicate("r", 1), Constant("z"))

        self.assertIn(atom_p, collection)
        self.assertIn(atom_q, collection)
        self.assertNotIn(atom_r, collection)

    def test_contains_unknown_predicate(self):
        """Test containment check for unknown predicate returns False."""
        collection = MaterializedDataCollection({self.p: self.fb1})
        atom_q = Atom(self.q, Constant("x"))
        self.assertNotIn(atom_q, collection)

    def test_variables_property(self):
        """Test variables property aggregates from all sources."""
        fb1 = FrozenInMemoryFactBase(
            self.parser.parse_atoms("p(X,a).")
        )
        fb2 = FrozenInMemoryFactBase(
            self.parser.parse_atoms("q(Y).")
        )
        collection = MaterializedDataCollection({
            self.p: fb1,
            self.q: fb2,
        })
        self.assertEqual(collection.variables, {Variable("X"), Variable("Y")})

    def test_constants_property(self):
        """Test constants property aggregates from all sources."""
        collection = MaterializedDataCollection({
            self.p: self.fb1,
            self.q: self.fb2,
        })
        expected = {
            Constant("a"), Constant("b"), Constant("c"), Constant("d"),
            Constant("x"), Constant("y"),
        }
        self.assertEqual(collection.constants, expected)

    def test_terms_property(self):
        """Test terms property aggregates from all sources."""
        fb1 = FrozenInMemoryFactBase(
            self.parser.parse_atoms("p(X,a).")
        )
        fb2 = FrozenInMemoryFactBase(
            self.parser.parse_atoms("q(Y).")
        )
        collection = MaterializedDataCollection({
            self.p: fb1,
            self.q: fb2,
        })
        expected = {Variable("X"), Variable("Y"), Constant("a")}
        self.assertEqual(collection.terms, expected)

    def test_term_caching(self):
        """Test that term properties are cached."""
        collection = MaterializedDataCollection({
            self.p: self.fb1,
            self.q: self.fb2,
        })
        # First access
        vars1 = collection.variables
        consts1 = collection.constants
        terms1 = collection.terms

        # Second access should return cached values (same object)
        self.assertIs(collection.variables, vars1)
        self.assertIs(collection.constants, consts1)
        self.assertIs(collection.terms, terms1)

    def test_non_materializable_source_raises(self):
        """Test that non-Materializable sources raise TypeError."""
        # Create a minimal Queryable that is not Materializable
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
            MaterializedDataCollection({self.p: source})

    def test_readable_data_functionality(self):
        """Test that ReadableData functionality still works."""
        collection = MaterializedDataCollection({
            self.p: self.fb1,
            self.q: self.fb2,
        })

        # Test get_predicates
        predicates = set(collection.get_predicates())
        self.assertEqual(predicates, {self.p, self.q})

        # Test has_predicate
        self.assertTrue(collection.has_predicate(self.p))
        self.assertTrue(collection.has_predicate(self.q))

        # Test evaluate
        query = BasicQuery(self.p, {}, {0: Variable("X"), 1: Variable("Y")})
        results = list(collection.evaluate(query))
        self.assertEqual(len(results), 2)

    def test_repr(self):
        """Test repr."""
        collection = MaterializedDataCollection({self.p: self.fb1})
        r = repr(collection)
        self.assertIn("MaterializedDataCollection", r)


class TestMaterializedDataCollectionWithMutable(unittest.TestCase):
    """Test MaterializedDataCollection with mutable sources."""

    def test_mutable_source(self):
        """Test collection works with mutable fact base."""
        parser = Dlgp2Parser.instance()
        p = Predicate("p", 2)

        fb = MutableInMemoryFactBase(parser.parse_atoms("p(a,b)."))
        collection = MaterializedDataCollection({p: fb})

        self.assertEqual(len(collection), 1)

        # Add to the underlying source
        fb.add(Atom(p, Constant("c"), Constant("d")))

        # Collection should reflect the change
        self.assertEqual(len(collection), 2)


if __name__ == "__main__":
    unittest.main()
