"""
Unit tests for session providers.
"""

import unittest
from unittest import TestCase

from prototyping_inference_engine.session.providers import (
    FactBaseFactoryProvider,
    RewritingAlgorithmProvider,
    ParserProvider,
    DefaultFactBaseFactoryProvider,
    DefaultRewritingAlgorithmProvider,
)
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.backward_chaining.breadth_first_rewriting import (
    BreadthFirstRewriting,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestDefaultFactBaseFactoryProvider(TestCase):
    """Tests for DefaultFactBaseFactoryProvider."""

    def test_implements_protocol(self):
        """Test that DefaultFactBaseFactoryProvider implements the protocol."""
        provider = DefaultFactBaseFactoryProvider()
        self.assertIsInstance(provider, FactBaseFactoryProvider)

    def test_create_mutable_returns_mutable_fact_base(self):
        """Test that create_mutable returns a MutableInMemoryFactBase."""
        provider = DefaultFactBaseFactoryProvider()
        fb = provider.create_mutable()
        self.assertIsInstance(fb, MutableInMemoryFactBase)

    def test_create_mutable_with_atoms(self):
        """Test that create_mutable can be initialized with atoms."""
        provider = DefaultFactBaseFactoryProvider()
        atoms = DlgpeParser.instance().parse_atoms("p(a,b). q(c).")
        fb = provider.create_mutable(atoms)
        self.assertEqual(len(fb), 2)

    def test_create_frozen_returns_frozen_fact_base(self):
        """Test that create_frozen returns a FrozenInMemoryFactBase."""
        provider = DefaultFactBaseFactoryProvider()
        fb = provider.create_frozen()
        self.assertIsInstance(fb, FrozenInMemoryFactBase)

    def test_create_frozen_with_atoms(self):
        """Test that create_frozen can be initialized with atoms."""
        provider = DefaultFactBaseFactoryProvider()
        atoms = DlgpeParser.instance().parse_atoms("p(a,b). q(c).")
        fb = provider.create_frozen(atoms)
        self.assertEqual(len(fb), 2)


class TestDefaultRewritingAlgorithmProvider(TestCase):
    """Tests for DefaultRewritingAlgorithmProvider."""

    def test_implements_protocol(self):
        """Test that DefaultRewritingAlgorithmProvider implements the protocol."""
        provider = DefaultRewritingAlgorithmProvider()
        self.assertIsInstance(provider, RewritingAlgorithmProvider)

    def test_get_algorithm_returns_breadth_first_rewriting(self):
        """Test that get_algorithm returns a BreadthFirstRewriting instance."""
        provider = DefaultRewritingAlgorithmProvider()
        algorithm = provider.get_algorithm()
        self.assertIsInstance(algorithm, BreadthFirstRewriting)

    def test_get_algorithm_returns_new_instance_each_time(self):
        """Test that get_algorithm returns a new instance each call."""
        provider = DefaultRewritingAlgorithmProvider()
        alg1 = provider.get_algorithm()
        alg2 = provider.get_algorithm()
        # They should be different instances
        self.assertIsNot(alg1, alg2)


class TestCustomProvider(TestCase):
    """Tests for custom provider implementations."""

    def test_custom_fact_base_provider(self):
        """Test that a custom provider can be created."""

        class CustomFactBaseProvider:
            def __init__(self):
                self.create_count = 0

            def create_mutable(self, atoms=None):
                self.create_count += 1
                return MutableInMemoryFactBase(atoms)

            def create_frozen(self, atoms=None):
                self.create_count += 1
                return FrozenInMemoryFactBase(atoms)

        provider = CustomFactBaseProvider()
        self.assertIsInstance(provider, FactBaseFactoryProvider)

        provider.create_mutable()
        provider.create_frozen()
        self.assertEqual(provider.create_count, 2)


class TestCustomParserProvider(TestCase):
    """Tests for custom parser provider implementations."""

    def test_custom_parser_provider(self):
        """Test that a custom parser provider can be created."""
        from prototyping_inference_engine.api.atom.atom import Atom
        from prototyping_inference_engine.api.atom.predicate import Predicate
        from prototyping_inference_engine.api.atom.term.constant import Constant

        class MockParserProvider:
            """A mock parser that returns fixed atoms."""

            def parse_atoms(self, text):
                # Return a fixed atom regardless of input
                p = Predicate("mock", 1)
                a = Constant("mock_const")
                return [Atom(p, a)]

            def parse_rules(self, text):
                return []

            def parse_conjunctive_queries(self, text):
                return []

            def parse_queries(self, text):
                return []

            def parse_union_conjunctive_queries(self, text):
                return []

            def parse_negative_constraints(self, text):
                return []

        provider = MockParserProvider()
        self.assertIsInstance(provider, ParserProvider)

        atoms = list(provider.parse_atoms("anything"))
        self.assertEqual(len(atoms), 1)
        self.assertEqual(atoms[0].predicate.name, "mock")


class TestDlgpeParserProvider(TestCase):
    """Tests for DlgpeParserProvider."""

    def test_implements_protocol(self):
        """Test that DlgpeParserProvider implements the protocol."""
        from prototyping_inference_engine.session.providers import DlgpeParserProvider

        provider = DlgpeParserProvider()
        self.assertIsInstance(provider, ParserProvider)

    def test_parse_atoms(self):
        """Test parsing atoms."""
        from prototyping_inference_engine.session.providers import DlgpeParserProvider

        provider = DlgpeParserProvider()
        atoms = list(provider.parse_atoms("p(a,b). q(c)."))
        self.assertEqual(len(atoms), 2)

    def test_parse_rules(self):
        """Test parsing rules."""
        from prototyping_inference_engine.session.providers import DlgpeParserProvider

        provider = DlgpeParserProvider()
        rules = list(provider.parse_rules("q(X) :- p(X,Y)."))
        self.assertEqual(len(rules), 1)

    def test_parse_queries(self):
        """Test parsing queries."""
        from prototyping_inference_engine.api.query.fo_query import FOQuery
        from prototyping_inference_engine.session.providers import DlgpeParserProvider

        provider = DlgpeParserProvider()
        queries = list(provider.parse_queries("?(X) :- p(X,Y)."))
        self.assertEqual(len(queries), 1)
        self.assertIsInstance(queries[0], FOQuery)

    def test_parse_conjunctive_queries(self):
        """Test parsing conjunctive queries when compatible."""
        from prototyping_inference_engine.api.query.conjunctive_query import (
            ConjunctiveQuery,
        )
        from prototyping_inference_engine.session.providers import DlgpeParserProvider

        provider = DlgpeParserProvider()
        cqs = list(provider.parse_conjunctive_queries("?(X) :- p(X,Y)."))
        self.assertEqual(len(cqs), 1)
        self.assertIsInstance(cqs[0], ConjunctiveQuery)

    def test_parse_negative_constraints(self):
        """Test parsing negative constraints."""
        from prototyping_inference_engine.session.providers import DlgpeParserProvider

        provider = DlgpeParserProvider()
        constraints = list(provider.parse_negative_constraints("! :- p(X), q(X)."))
        self.assertEqual(len(constraints), 1)


if __name__ == "__main__":
    unittest.main()
