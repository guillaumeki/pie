"""
Unit tests for session support classes (ParseResult, SessionCleanupStats).
"""

import unittest
from unittest import TestCase

from prototyping_inference_engine.session.parse_result import ParseResult
from prototyping_inference_engine.session.cleanup_stats import SessionCleanupStats
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestParseResult(TestCase):
    """Tests for ParseResult dataclass."""

    def test_create_empty_result(self):
        """Test creating an empty ParseResult."""
        result = ParseResult(
            facts=FrozenAtomSet([]),
            rules=frozenset(),
            queries=frozenset(),
            constraints=frozenset(),
        )
        self.assertTrue(result.is_empty)
        self.assertFalse(result.has_facts)
        self.assertFalse(result.has_rules)
        self.assertFalse(result.has_queries)
        self.assertFalse(result.has_constraints)

    def test_create_result_with_facts(self):
        """Test creating a ParseResult with facts."""
        atoms = DlgpeParser.instance().parse_atoms("p(a,b). q(c).")
        result = ParseResult(
            facts=FrozenAtomSet(atoms),
            rules=frozenset(),
            queries=frozenset(),
            constraints=frozenset(),
        )
        self.assertFalse(result.is_empty)
        self.assertTrue(result.has_facts)
        self.assertEqual(len(result.facts), 2)

    def test_create_result_with_rules(self):
        """Test creating a ParseResult with rules."""
        rules = set(DlgpeParser.instance().parse_rules("q(X) :- p(X,Y)."))
        result = ParseResult(
            facts=FrozenAtomSet([]),
            rules=frozenset(rules),
            queries=frozenset(),
            constraints=frozenset(),
        )
        self.assertFalse(result.is_empty)
        self.assertTrue(result.has_rules)
        self.assertEqual(len(result.rules), 1)

    def test_create_result_with_queries(self):
        """Test creating a ParseResult with queries."""
        queries = set(DlgpeParser.instance().parse_queries("?(X) :- p(X,Y)."))
        result = ParseResult(
            facts=FrozenAtomSet([]),
            rules=frozenset(),
            queries=frozenset(queries),
            constraints=frozenset(),
        )
        self.assertFalse(result.is_empty)
        self.assertTrue(result.has_queries)
        self.assertEqual(len(result.queries), 1)

    def test_is_immutable(self):
        """Test that ParseResult is immutable."""
        result = ParseResult(
            facts=FrozenAtomSet([]),
            rules=frozenset(),
            queries=frozenset(),
            constraints=frozenset(),
        )
        with self.assertRaises(AttributeError):
            result.facts = FrozenAtomSet([])

    def test_equality(self):
        """Test that ParseResult supports equality comparison."""
        atoms = list(DlgpeParser.instance().parse_atoms("p(a)."))
        result1 = ParseResult(
            facts=FrozenAtomSet(atoms),
            rules=frozenset(),
            queries=frozenset(),
            constraints=frozenset(),
            base_iri="http://example.org/base/",
            prefixes=(("ex", "http://example.org/ns/"),),
        )
        result2 = ParseResult(
            facts=FrozenAtomSet(atoms),
            rules=frozenset(),
            queries=frozenset(),
            constraints=frozenset(),
            base_iri="http://example.org/base/",
            prefixes=(("ex", "http://example.org/ns/"),),
        )
        self.assertEqual(result1, result2)


class TestSessionCleanupStats(TestCase):
    """Tests for SessionCleanupStats dataclass."""

    def test_create_empty_stats(self):
        """Test creating empty cleanup stats."""
        stats = SessionCleanupStats(
            variables_removed=0,
            constants_removed=0,
            predicates_removed=0,
        )
        self.assertEqual(stats.total_removed, 0)
        self.assertTrue(stats.is_empty)

    def test_create_stats_with_values(self):
        """Test creating cleanup stats with values."""
        stats = SessionCleanupStats(
            variables_removed=5,
            constants_removed=3,
            predicates_removed=2,
        )
        self.assertEqual(stats.variables_removed, 5)
        self.assertEqual(stats.constants_removed, 3)
        self.assertEqual(stats.predicates_removed, 2)
        self.assertEqual(stats.total_removed, 10)
        self.assertFalse(stats.is_empty)

    def test_addition(self):
        """Test adding two cleanup stats together."""
        stats1 = SessionCleanupStats(
            variables_removed=5,
            constants_removed=3,
            predicates_removed=2,
        )
        stats2 = SessionCleanupStats(
            variables_removed=2,
            constants_removed=1,
            predicates_removed=3,
        )
        combined = stats1 + stats2
        self.assertEqual(combined.variables_removed, 7)
        self.assertEqual(combined.constants_removed, 4)
        self.assertEqual(combined.predicates_removed, 5)
        self.assertEqual(combined.total_removed, 16)

    def test_addition_returns_new_instance(self):
        """Test that addition returns a new instance."""
        stats1 = SessionCleanupStats(1, 1, 1)
        stats2 = SessionCleanupStats(2, 2, 2)
        combined = stats1 + stats2
        self.assertIsNot(combined, stats1)
        self.assertIsNot(combined, stats2)

    def test_addition_with_invalid_type(self):
        """Test that addition with invalid type returns NotImplemented."""
        stats = SessionCleanupStats(1, 1, 1)
        result = stats.__add__("invalid")
        self.assertEqual(result, NotImplemented)

    def test_is_immutable(self):
        """Test that SessionCleanupStats is immutable."""
        stats = SessionCleanupStats(1, 2, 3)
        with self.assertRaises(AttributeError):
            stats.variables_removed = 10

    def test_repr(self):
        """Test string representation."""
        stats = SessionCleanupStats(5, 3, 2)
        self.assertEqual(stats.variables_removed, 5)
        self.assertEqual(stats.constants_removed, 3)
        self.assertEqual(stats.predicates_removed, 2)
        self.assertEqual(stats.total_removed, 10)

    def test_equality(self):
        """Test that SessionCleanupStats supports equality comparison."""
        stats1 = SessionCleanupStats(1, 2, 3)
        stats2 = SessionCleanupStats(1, 2, 3)
        stats3 = SessionCleanupStats(1, 2, 4)
        self.assertEqual(stats1, stats2)
        self.assertNotEqual(stats1, stats3)


if __name__ == "__main__":
    unittest.main()
