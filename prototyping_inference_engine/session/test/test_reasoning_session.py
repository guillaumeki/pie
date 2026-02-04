"""
Unit tests for ReasoningSession.
"""

import unittest
from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.factory import (
    VariableFactory,
    ConstantFactory,
    PredicateFactory,
)
from prototyping_inference_engine.api.atom.term.storage import DictStorage
from prototyping_inference_engine.api.atom.predicate import comparison_predicate
from prototyping_inference_engine.api.data.comparison_data import ComparisonDataSource
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.session import (
    ParseResult,
    SessionCleanupStats,
    ParserProvider,
)
from prototyping_inference_engine.session.term_factories import TermFactories
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestReasoningSessionCreate(TestCase):
    """Tests for ReasoningSession.create() factory method."""

    def test_create_with_defaults(self):
        """Test creating a session with default settings."""
        session = ReasoningSession.create()
        self.assertFalse(session.is_closed)
        self.assertIn(Variable, session.term_factories)
        self.assertIn(Constant, session.term_factories)
        self.assertIn(Predicate, session.term_factories)
        session.close()

    def test_create_with_auto_cleanup_true(self):
        """Test creating a session with auto_cleanup=True."""
        session = ReasoningSession.create(auto_cleanup=True)
        self.assertFalse(session.is_closed)
        session.close()

    def test_create_with_auto_cleanup_false(self):
        """Test creating a session with auto_cleanup=False."""
        session = ReasoningSession.create(auto_cleanup=False)
        self.assertFalse(session.is_closed)
        session.close()


class TestReasoningSessionCustomFactories(TestCase):
    """Tests for ReasoningSession with custom factories."""

    def test_create_with_custom_term_factories(self):
        """Test creating a session with custom term factories."""
        factories = TermFactories()
        factories.register(Variable, VariableFactory(DictStorage()))
        factories.register(Constant, ConstantFactory(DictStorage()))
        factories.register(Predicate, PredicateFactory(DictStorage()))

        session = ReasoningSession(term_factories=factories)
        self.assertIs(session.term_factories, factories)
        session.close()

    def test_extensible_with_new_term_type(self):
        """Test that session is extensible with new term types (OCP)."""

        # Simulate a new term type with a mock factory
        class MockTermType:
            pass

        class MockTermFactory:
            def __init__(self):
                self.created = []

            def create(self, *args):
                obj = MockTermType()
                self.created.append(obj)
                return obj

        factories = TermFactories()
        factories.register(Variable, VariableFactory(DictStorage()))
        factories.register(Constant, ConstantFactory(DictStorage()))
        factories.register(Predicate, PredicateFactory(DictStorage()))
        factories.register(MockTermType, MockTermFactory())

        session = ReasoningSession(term_factories=factories)

        # Can access the new factory through the registry
        mock_factory = session.term_factories.get(MockTermType)
        term = mock_factory.create("test")
        self.assertIsInstance(term, MockTermType)
        self.assertEqual(len(mock_factory.created), 1)

        session.close()

    def test_extensible_with_custom_parser(self):
        """Test that session is extensible with custom parser (OCP)."""

        class MockParserProvider:
            """A mock parser that returns fixed atoms."""

            def __init__(self):
                self.parse_calls = 0

            def parse_atoms(self, text):
                self.parse_calls += 1
                p = Predicate("mock", 1)
                a = Constant("mock_const")
                return [Atom(p, a)]

            def parse_rules(self, text):
                return []

            def parse_conjunctive_queries(self, text):
                return []

            def parse_union_conjunctive_queries(self, text):
                return []

            def parse_queries(self, text):
                return []

            def parse_negative_constraints(self, text):
                return []

        mock_parser = MockParserProvider()
        self.assertIsInstance(mock_parser, ParserProvider)

        session = ReasoningSession.create(parser_provider=mock_parser)

        # Parse should use the mock parser
        result = session.parse("anything - this will be ignored")
        self.assertEqual(mock_parser.parse_calls, 1)
        self.assertEqual(len(result.facts), 1)

        # Verify it parsed the mock atom
        atom = next(iter(result.facts))
        self.assertEqual(atom.predicate.name, "mock")

        session.close()


class TestReasoningSessionTermCreation(TestCase):
    """Tests for term creation methods."""

    def setUp(self):
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()

    def test_variable_creation(self):
        """Test creating variables."""
        x = self.session.variable("X")
        self.assertIsInstance(x, Variable)
        self.assertEqual(str(x), "X")

    def test_variable_same_identifier_same_instance(self):
        """Test that same identifier returns same instance."""
        x1 = self.session.variable("X")
        x2 = self.session.variable("X")
        self.assertIs(x1, x2)

    def test_constant_creation(self):
        """Test creating constants."""
        a = self.session.constant("a")
        self.assertIsInstance(a, Constant)
        self.assertEqual(str(a), "a")

    def test_predicate_creation(self):
        """Test creating predicates."""
        p = self.session.predicate("p", 2)
        self.assertIsInstance(p, Predicate)
        self.assertEqual(p.name, "p")
        self.assertEqual(p.arity, 2)

    def test_fresh_variable(self):
        """Test creating fresh variables."""
        v1 = self.session.fresh_variable()
        v2 = self.session.fresh_variable()
        self.assertIsNot(v1, v2)
        self.assertNotEqual(str(v1), str(v2))

    def test_atom_creation(self):
        """Test creating atoms."""
        p = self.session.predicate("p", 2)
        x = self.session.variable("X")
        a = self.session.constant("a")
        atom = self.session.atom(p, x, a)
        self.assertIsInstance(atom, Atom)
        self.assertEqual(atom.predicate, p)
        self.assertEqual(atom.terms, (x, a))


class TestReasoningSessionParsing(TestCase):
    """Tests for session parsing."""

    def setUp(self):
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()

    def test_parse_facts(self):
        """Test parsing facts."""
        result = self.session.parse("p(a,b). q(c).")
        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.facts), 2)
        self.assertTrue(result.has_facts)

    def test_parse_rules(self):
        """Test parsing rules."""
        result = self.session.parse("q(X) :- p(X,Y).")
        self.assertEqual(len(result.rules), 1)
        self.assertTrue(result.has_rules)

    def test_parse_queries(self):
        """Test parsing queries."""
        result = self.session.parse("?(X) :- p(X,Y).")
        # Parser returns both CQ and UCQ versions of the same query
        self.assertGreaterEqual(len(result.queries), 1)
        self.assertTrue(result.has_queries)

    def test_parse_tracks_terms(self):
        """Test that parsing tracks terms in the session."""
        self.session.parse("p(a,b). q(X) :- r(X,Y).")

        # Terms should be tracked
        var_factory = self.session.term_factories.get(Variable)
        const_factory = self.session.term_factories.get(Constant)
        pred_factory = self.session.term_factories.get(Predicate)

        self.assertGreater(len(var_factory), 0)
        self.assertGreater(len(const_factory), 0)
        self.assertGreater(len(pred_factory), 0)

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = self.session.parse("")
        self.assertTrue(result.is_empty)


class TestReasoningSessionEvaluationWithSources(TestCase):
    """Tests for query evaluation with extra sources."""

    def setUp(self):
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()

    def test_evaluate_query_with_comparison_source(self):
        left = self.session.literal("1", "xsd:integer")
        right = self.session.literal("2", "xsd:integer")
        atom = Atom(comparison_predicate("<"), left, right)
        query = FOQuery(atom, answer_variables=[])
        data_source = ComparisonDataSource(self.session.literal_config.comparison)
        fact_base = self.session.create_fact_base([])
        results = list(
            self.session.evaluate_query_with_sources(query, fact_base, [data_source])
        )
        self.assertEqual(results, [tuple()])

    def test_evaluate_query_with_function_term(self):
        def add(a: int, b: int) -> int:
            return a + b

        self.session.register_python_function("add", add, mode="python")
        p = self.session.predicate("p", 1)
        lit_two = self.session.literal("2", "xsd:integer")
        fact_base = self.session.create_fact_base([Atom(p, lit_two)])

        result = self.session.parse("?( ) :- p(add(1,1)).")
        query = next(iter(result.queries))
        answers = list(
            self.session.evaluate_query_with_sources(query, fact_base, result.sources)
        )
        self.assertEqual(answers, [tuple()])


class TestReasoningSessionFactBase(TestCase):
    """Tests for fact base creation."""

    def setUp(self):
        self.session = ReasoningSession.create()

    def tearDown(self):
        self.session.close()

    def test_create_empty_fact_base(self):
        """Test creating an empty fact base."""
        fb = self.session.create_fact_base()
        self.assertEqual(len(fb), 0)
        self.assertIn(fb, self.session.fact_bases)

    def test_create_fact_base_with_atoms(self):
        """Test creating a fact base with initial atoms."""
        p = self.session.predicate("p", 1)
        a = self.session.constant("a")
        atom = self.session.atom(p, a)
        fb = self.session.create_fact_base([atom])
        self.assertEqual(len(fb), 1)

    def test_fact_bases_tracked(self):
        """Test that created fact bases are tracked."""
        fb1 = self.session.create_fact_base()
        fb2 = self.session.create_fact_base()
        self.assertEqual(len(self.session.fact_bases), 2)
        self.assertIn(fb1, self.session.fact_bases)
        self.assertIn(fb2, self.session.fact_bases)


class TestReasoningSessionOntology(TestCase):
    """Tests for ontology creation."""

    def setUp(self):
        self.session = ReasoningSession.create()

    def tearDown(self):
        self.session.close()

    def test_create_empty_ontology(self):
        """Test creating an empty ontology."""
        onto = self.session.create_ontology()
        self.assertEqual(len(onto.rules), 0)
        self.assertIn(onto, self.session.ontologies)

    def test_create_ontology_with_rules(self):
        """Test creating an ontology with rules."""
        result = self.session.parse("q(X) :- p(X,Y).")
        onto = self.session.create_ontology(rules=result.rules)
        self.assertEqual(len(onto.rules), 1)

    def test_ontologies_tracked(self):
        """Test that created ontologies are tracked."""
        _ = self.session.create_ontology()
        _ = self.session.create_ontology()
        self.assertEqual(len(self.session.ontologies), 2)


class TestReasoningSessionRewriting(TestCase):
    """Tests for query rewriting."""

    def setUp(self):
        from prototyping_inference_engine.session.providers import Dlgp2ParserProvider

        self.session = ReasoningSession.create(parser_provider=Dlgp2ParserProvider())

    def tearDown(self):
        self.session.close()

    def test_rewrite_conjunctive_query(self):
        """Test rewriting a conjunctive query."""
        result = self.session.parse("""
            q(X) :- p(X,Y).
            ?(X) :- q(X).
        """)
        query = next(iter(result.queries))
        rewritten = self.session.rewrite(query, result.rules, step_limit=1)
        self.assertIsNotNone(rewritten)

    def test_rewrite_with_limit(self):
        """Test rewriting with step limit."""
        result = self.session.parse("""
            q(X) :- p(X,Y).
            ?(X) :- q(X).
        """)
        query = next(iter(result.queries))
        rewritten = self.session.rewrite(query, result.rules, step_limit=0)
        # With limit=0, should return the original query
        self.assertIsNotNone(rewritten)


class TestReasoningSessionLifecycle(TestCase):
    """Tests for session lifecycle management."""

    def test_context_manager(self):
        """Test using session as context manager."""
        with ReasoningSession.create() as session:
            self.assertFalse(session.is_closed)
            session.variable("X")
        self.assertTrue(session.is_closed)

    def test_close_idempotent(self):
        """Test that close() can be called multiple times."""
        session = ReasoningSession.create()
        session.close()
        session.close()  # Should not raise
        self.assertTrue(session.is_closed)

    def test_operations_on_closed_session_raise(self):
        """Test that operations on closed session raise error."""
        session = ReasoningSession.create()
        session.close()

        with self.assertRaises(RuntimeError):
            session.variable("X")

        with self.assertRaises(RuntimeError):
            session.constant("a")

        with self.assertRaises(RuntimeError):
            session.parse("p(a).")

        with self.assertRaises(RuntimeError):
            session.create_fact_base()

    def test_cleanup_returns_stats(self):
        """Test that cleanup returns statistics."""
        session = ReasoningSession.create(auto_cleanup=False)
        session.variable("X")
        session.constant("a")
        stats = session.cleanup()
        self.assertIsInstance(stats, SessionCleanupStats)
        session.close()


class TestTermFactories(TestCase):
    """Tests for TermFactories registry."""

    def test_register_and_get(self):
        """Test registering and getting factories."""
        factories = TermFactories()
        var_factory = VariableFactory(DictStorage())
        factories.register(Variable, var_factory)

        retrieved = factories.get(Variable)
        self.assertIs(retrieved, var_factory)

    def test_get_unregistered_raises(self):
        """Test that getting unregistered type raises KeyError."""
        factories = TermFactories()
        with self.assertRaises(KeyError):
            factories.get(Variable)

    def test_has_and_contains(self):
        """Test has() and __contains__."""
        factories = TermFactories()
        self.assertFalse(factories.has(Variable))
        self.assertNotIn(Variable, factories)

        factories.register(Variable, VariableFactory(DictStorage()))
        self.assertTrue(factories.has(Variable))
        self.assertIn(Variable, factories)

    def test_len_and_iter(self):
        """Test len() and iteration."""
        factories = TermFactories()
        self.assertEqual(len(factories), 0)

        factories.register(Variable, VariableFactory(DictStorage()))
        factories.register(Constant, ConstantFactory(DictStorage()))
        self.assertEqual(len(factories), 2)

        types = list(factories)
        self.assertIn(Variable, types)
        self.assertIn(Constant, types)

    def test_registered_types(self):
        """Test registered_types()."""
        factories = TermFactories()
        factories.register(Variable, VariableFactory(DictStorage()))
        factories.register(Constant, ConstantFactory(DictStorage()))

        types = factories.registered_types()
        self.assertEqual(types, {Variable, Constant})

    def test_clear(self):
        """Test clear()."""
        factories = TermFactories()
        factories.register(Variable, VariableFactory(DictStorage()))
        factories.clear()
        self.assertEqual(len(factories), 0)


if __name__ == "__main__":
    unittest.main()
