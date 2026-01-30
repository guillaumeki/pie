"""
Tests for FOQueryEvaluator.
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.api.formula.existential_formula import ExistentialFormula
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.fo_query_evaluator import FOQueryEvaluator
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import FormulaEvaluatorRegistry
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestFOQueryEvaluator(unittest.TestCase):
    """Test FOQueryEvaluator."""

    def setUp(self):
        FormulaEvaluatorRegistry.reset()
        self.evaluator = FOQueryEvaluator()
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.a = Constant("a")
        self.b = Constant("b")
        self.c = Constant("c")

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    def test_evaluate_atomic_query_single_answer(self):
        # Fact base: {p(a, b)}
        # Query: ?(X) :- p(a, X)
        # Expected: (b,)
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        query = FOQuery(Atom(self.p, self.a, self.x), [self.x])

        results = list(self.evaluator.evaluate(query, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (self.b,))

    def test_evaluate_atomic_query_multiple_answers(self):
        # Fact base: {p(a, b), p(a, c)}
        # Query: ?(X) :- p(a, X)
        # Expected: (b,), (c,)
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a, self.b),
            Atom(self.p, self.a, self.c),
        ])
        query = FOQuery(Atom(self.p, self.a, self.x), [self.x])

        results = list(self.evaluator.evaluate(query, fact_base))

        self.assertEqual(len(results), 2)
        result_set = set(results)
        self.assertIn((self.b,), result_set)
        self.assertIn((self.c,), result_set)

    def test_evaluate_atomic_query_multiple_answer_vars(self):
        # Fact base: {p(a, b), p(b, c)}
        # Query: ?(X, Y) :- p(X, Y)
        # Expected: (a, b), (b, c)
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a, self.b),
            Atom(self.p, self.b, self.c),
        ])
        query = FOQuery(Atom(self.p, self.x, self.y), [self.x, self.y])

        results = list(self.evaluator.evaluate(query, fact_base))

        self.assertEqual(len(results), 2)
        result_set = set(results)
        self.assertIn((self.a, self.b), result_set)
        self.assertIn((self.b, self.c), result_set)

    def test_evaluate_boolean_query_true(self):
        # Fact base: {p(a, b)}
        # Query: ?() :- p(a, b)
        # Expected: one empty tuple (true)
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        query = FOQuery(Atom(self.p, self.a, self.b), [])

        results = list(self.evaluator.evaluate(query, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ())

    def test_evaluate_boolean_query_false(self):
        # Fact base: {p(a, b)}
        # Query: ?() :- p(a, c)
        # Expected: no results (false)
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        query = FOQuery(Atom(self.p, self.a, self.c), [])

        results = list(self.evaluator.evaluate(query, fact_base))

        self.assertEqual(len(results), 0)

    def test_evaluate_no_matches(self):
        # Fact base: {p(a, b)}
        # Query: ?(X) :- q(X)
        # Expected: no results
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        query = FOQuery(Atom(self.q, self.x), [self.x])

        results = list(self.evaluator.evaluate(query, fact_base))

        self.assertEqual(len(results), 0)

    def test_evaluate_deduplicates_answers(self):
        # Fact base: {p(a, b), p(a, b)} (duplicate)
        # Actually MutableInMemoryFactBase uses a set, so let's test differently
        # Fact base: {p(a, b), p(a, c)}
        # Query: ?(X) :- ∃Y.p(X, Y)  (Y is projected out, so X=a appears twice)
        # Expected: (a,) - deduplicated
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a, self.b),
            Atom(self.p, self.a, self.c),
        ])
        formula = ExistentialFormula(self.y, Atom(self.p, self.x, self.y))
        query = FOQuery(formula, [self.x])

        results = list(self.evaluator.evaluate(query, fact_base))

        # Should be deduplicated to just (a,)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (self.a,))


class TestFOQueryEvaluatorWithSession(unittest.TestCase):
    """Test FOQueryEvaluator via ReasoningSession."""

    def setUp(self):
        FormulaEvaluatorRegistry.reset()
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()
        FormulaEvaluatorRegistry.reset()

    def test_evaluate_query_from_session(self):
        # Create fact base
        result = self.session.parse("p(a, b). p(a, c). p(b, c).")
        fb = self.session.create_fact_base(result.facts)

        # Create query: ?(X) :- p(a, X)
        query = (self.session.fo_query().builder()
            .answer("X")
            .atom("p", "a", "X")
            .build())

        # Evaluate
        results = list(self.session.evaluate_query(query, fb))

        self.assertEqual(len(results), 2)
        # Results should contain constants b and c
        result_values = {r[0].identifier for r in results}
        self.assertEqual(result_values, {"b", "c"})

    def test_full_workflow(self):
        # Parse facts
        result = self.session.parse("""
            parent(alice, bob).
            parent(alice, carol).
            parent(bob, dave).
        """)
        fb = self.session.create_fact_base(result.facts)

        # Query: Who are Alice's children?
        # ?(X) :- parent(alice, X)
        query = (self.session.fo_query().builder()
            .answer("X")
            .atom("parent", "alice", "X")
            .build())

        results = list(self.session.evaluate_query(query, fb))

        self.assertEqual(len(results), 2)
        names = {r[0].identifier for r in results}
        self.assertEqual(names, {"bob", "carol"})

    def test_boolean_query_via_session(self):
        result = self.session.parse("p(a, b).")
        fb = self.session.create_fact_base(result.facts)

        # Boolean query: ?() :- p(a, b)
        query = (self.session.fo_query().builder()
            .atom("p", "a", "b")
            .build())

        results = list(self.session.evaluate_query(query, fb))

        # Should return one empty tuple (query is satisfied)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ())


if __name__ == "__main__":
    unittest.main()
