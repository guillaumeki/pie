"""Tests for ReadableDataCollection."""

import unittest

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.collection.readable_collection import (
    ReadableDataCollection,
)
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestReadableDataCollection(unittest.TestCase):
    """Test ReadableDataCollection."""

    def setUp(self):
        self.parser = Dlgp2Parser.instance()
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.r = Predicate("r", 2)

        # Create two fact bases with different predicates
        self.fb1 = FrozenInMemoryFactBase(self.parser.parse_atoms("p(a,b), p(c,d)."))
        self.fb2 = FrozenInMemoryFactBase(self.parser.parse_atoms("q(x), q(y)."))

    def test_empty_collection(self):
        """Test empty collection."""
        collection = ReadableDataCollection({})
        self.assertEqual(list(collection.get_predicates()), [])

    def test_single_source(self):
        """Test collection with a single source."""
        collection = ReadableDataCollection({self.p: self.fb1})
        self.assertTrue(collection.has_predicate(self.p))
        self.assertFalse(collection.has_predicate(self.q))

    def test_multiple_sources(self):
        """Test collection with multiple sources."""
        collection = ReadableDataCollection(
            {
                self.p: self.fb1,
                self.q: self.fb2,
            }
        )
        self.assertTrue(collection.has_predicate(self.p))
        self.assertTrue(collection.has_predicate(self.q))
        self.assertFalse(collection.has_predicate(self.r))

    def test_get_predicates(self):
        """Test get_predicates returns all predicates."""
        collection = ReadableDataCollection(
            {
                self.p: self.fb1,
                self.q: self.fb2,
            }
        )
        predicates = set(collection.get_predicates())
        self.assertEqual(predicates, {self.p, self.q})

    def test_get_atomic_pattern(self):
        """Test get_atomic_pattern delegates to source."""
        collection = ReadableDataCollection({self.p: self.fb1})
        pattern = collection.get_atomic_pattern(self.p)
        self.assertEqual(pattern.predicate, self.p)

    def test_get_atomic_pattern_unknown_predicate(self):
        """Test get_atomic_pattern raises KeyError for unknown predicate."""
        collection = ReadableDataCollection({self.p: self.fb1})
        with self.assertRaises(KeyError):
            collection.get_atomic_pattern(self.q)

    def test_evaluate_routes_to_correct_source(self):
        """Test evaluate routes query to the correct source."""
        collection = ReadableDataCollection(
            {
                self.p: self.fb1,
                self.q: self.fb2,
            }
        )

        # Query p predicate - should route to fb1
        query = BasicQuery(
            self.p,
            bound_positions={},
            answer_variables={0: Variable("X"), 1: Variable("Y")},
        )
        results = list(collection.evaluate(query))
        self.assertEqual(len(results), 2)
        self.assertIn((Constant("a"), Constant("b")), results)
        self.assertIn((Constant("c"), Constant("d")), results)

        # Query q predicate - should route to fb2
        query2 = BasicQuery(
            self.q,
            bound_positions={},
            answer_variables={0: Variable("Z")},
        )
        results2 = list(collection.evaluate(query2))
        self.assertEqual(len(results2), 2)
        self.assertIn((Constant("x"),), results2)
        self.assertIn((Constant("y"),), results2)

    def test_evaluate_with_bound_positions(self):
        """Test evaluate with bound positions filters correctly."""
        collection = ReadableDataCollection({self.p: self.fb1})

        query = BasicQuery(
            self.p,
            bound_positions={0: Constant("a")},
            answer_variables={1: Variable("Y")},
        )
        results = list(collection.evaluate(query))
        self.assertEqual(results, [(Constant("b"),)])

    def test_evaluate_unknown_predicate(self):
        """Test evaluate raises KeyError for unknown predicate."""
        collection = ReadableDataCollection({self.p: self.fb1})
        query = BasicQuery(self.q, {}, {0: Variable("X")})
        with self.assertRaises(KeyError):
            list(collection.evaluate(query))

    def test_can_evaluate(self):
        """Test can_evaluate delegates to source."""
        collection = ReadableDataCollection({self.p: self.fb1})

        query = BasicQuery(self.p, {}, {0: Variable("X"), 1: Variable("Y")})
        self.assertTrue(collection.can_evaluate(query))

    def test_can_evaluate_unknown_predicate(self):
        """Test can_evaluate returns False for unknown predicate."""
        collection = ReadableDataCollection({self.p: self.fb1})
        query = BasicQuery(self.q, {}, {0: Variable("X")})
        self.assertFalse(collection.can_evaluate(query))

    def test_sources_property(self):
        """Test sources property returns copy of mapping."""
        collection = ReadableDataCollection({self.p: self.fb1})
        sources = collection.sources
        self.assertEqual(sources, {self.p: self.fb1})
        # Verify it's a copy
        sources[self.q] = self.fb2
        self.assertNotIn(self.q, collection.sources)

    def test_get_source_for_predicate(self):
        """Test get_source_for_predicate returns correct source."""
        collection = ReadableDataCollection(
            {
                self.p: self.fb1,
                self.q: self.fb2,
            }
        )
        self.assertIs(collection.get_source_for_predicate(self.p), self.fb1)
        self.assertIs(collection.get_source_for_predicate(self.q), self.fb2)
        self.assertIsNone(collection.get_source_for_predicate(self.r))

    def test_repr(self):
        """Test repr."""
        collection = ReadableDataCollection({self.p: self.fb1})
        r = repr(collection)
        self.assertIn("ReadableDataCollection", r)


class TestDynamicPredicates(unittest.TestCase):
    """Test dynamic predicate handling."""

    def test_dynamic_source_predicates_discovered(self):
        """Test that predicates from dynamic sources are discovered."""
        parser = Dlgp2Parser.instance()
        p = Predicate("p", 2)
        q = Predicate("q", 1)

        # fb1 is static, fb2 is dynamic
        fb1 = FrozenInMemoryFactBase(parser.parse_atoms("p(a,b)."))
        fb2 = FrozenInMemoryFactBase(parser.parse_atoms("q(x)."))

        collection = ReadableDataCollection(
            sources={p: fb1},
            dynamic_sources=[fb2],
        )

        # q should be discovered from dynamic source
        self.assertTrue(collection.has_predicate(q))
        self.assertIs(collection.get_source_for_predicate(q), fb2)

    def test_dynamic_source_evaluate(self):
        """Test evaluate works for predicates discovered from dynamic sources."""
        parser = Dlgp2Parser.instance()
        p = Predicate("p", 2)
        q = Predicate("q", 1)

        fb1 = FrozenInMemoryFactBase(parser.parse_atoms("p(a,b)."))
        fb2 = FrozenInMemoryFactBase(parser.parse_atoms("q(x), q(y)."))

        collection = ReadableDataCollection(
            sources={p: fb1},
            dynamic_sources=[fb2],
        )

        query = BasicQuery(q, {}, {0: Variable("X")})
        results = list(collection.evaluate(query))
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
