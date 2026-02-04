"""
Tests for UnionQueryEvaluator.
"""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator_registry import (
    QueryEvaluatorRegistry,
)
from prototyping_inference_engine.query_evaluation.evaluator.query.union_query_evaluator import (
    UnionQueryEvaluator,
)


class TestUnionQueryEvaluator(unittest.TestCase):
    """Test UnionQueryEvaluator."""

    def setUp(self):
        QueryEvaluatorRegistry.reset()
        self.registry = QueryEvaluatorRegistry.instance()
        self.evaluator = UnionQueryEvaluator(self.registry)

        # Predicates
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.r = Predicate("r", 2)

        # Variables
        self.x = Variable("X")
        self.y = Variable("Y")

        # Constants
        self.a = Constant("a")
        self.b = Constant("b")
        self.c = Constant("c")

    def tearDown(self):
        QueryEvaluatorRegistry.reset()

    def test_single_query_union(self):
        """
        UnionQuery with single FOQuery.
        Query: p(X) (single disjunct)
        FactBase: {p(a), p(b)}
        Expected: {X→a}, {X→b}
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.p, self.b),
            ]
        )

        foq = FOQuery(Atom(self.p, self.x), [self.x])
        uq = UnionQuery([foq], [self.x])

        results = list(self.evaluator.evaluate(uq, fact_base))

        self.assertEqual(len(results), 2)
        x_values = {r[self.x] for r in results}
        self.assertEqual(x_values, {self.a, self.b})

    def test_two_query_union(self):
        """
        UnionQuery with two FOQueries.
        Query: p(X) ∨ q(X)
        FactBase: {p(a), q(b)}
        Expected: {X→a}, {X→b}
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.q, self.b),
            ]
        )

        foq1 = FOQuery(Atom(self.p, self.x), [self.x])
        foq2 = FOQuery(Atom(self.q, self.x), [self.x])
        uq = UnionQuery([foq1, foq2], [self.x])

        results = list(self.evaluator.evaluate(uq, fact_base))

        self.assertEqual(len(results), 2)
        x_values = {r[self.x] for r in results}
        self.assertEqual(x_values, {self.a, self.b})

    def test_union_with_overlap(self):
        """
        UnionQuery where both disjuncts match the same data.
        Query: p(X) ∨ q(X)
        FactBase: {p(a), q(a)}
        Expected: {X→a} (deduplicated)
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.q, self.a),
            ]
        )

        foq1 = FOQuery(Atom(self.p, self.x), [self.x])
        foq2 = FOQuery(Atom(self.q, self.x), [self.x])
        uq = UnionQuery([foq1, foq2], [self.x])

        results = list(self.evaluator.evaluate(uq, fact_base))

        # Should be deduplicated
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)

    def test_union_no_match(self):
        """
        UnionQuery with no matches.
        Query: p(X) ∨ q(X)
        FactBase: {r(a, b)}
        Expected: empty
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
            ]
        )

        foq1 = FOQuery(Atom(self.p, self.x), [self.x])
        foq2 = FOQuery(Atom(self.q, self.x), [self.x])
        uq = UnionQuery([foq1, foq2], [self.x])

        results = list(self.evaluator.evaluate(uq, fact_base))

        self.assertEqual(len(results), 0)

    def test_evaluate_and_project(self):
        """
        Test evaluate_and_project method.
        Query: p(X) ∨ q(X)
        FactBase: {p(a), q(b)}
        Expected: (a,), (b,)
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.q, self.b),
            ]
        )

        foq1 = FOQuery(Atom(self.p, self.x), [self.x])
        foq2 = FOQuery(Atom(self.q, self.x), [self.x])
        uq = UnionQuery([foq1, foq2], [self.x])

        results = list(self.evaluator.evaluate_and_project(uq, fact_base))

        self.assertEqual(len(results), 2)
        result_set = set(results)
        self.assertIn((self.a,), result_set)
        self.assertIn((self.b,), result_set)

    def test_boolean_query(self):
        """
        Boolean UnionQuery (no answer variables).
        Query: p(a) ∨ q(b)
        FactBase: {p(a)}
        Expected: one result (true)
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
            ]
        )

        foq1 = FOQuery(Atom(self.p, self.a), [])
        foq2 = FOQuery(Atom(self.q, self.b), [])
        uq = UnionQuery([foq1, foq2], [])

        results = list(self.evaluator.evaluate(uq, fact_base))

        # At least one disjunct is satisfied
        self.assertEqual(len(results), 1)

    def test_empty_union(self):
        """
        Empty UnionQuery (no disjuncts).
        Expected: no results
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
            ]
        )

        uq = UnionQuery([], [self.x])

        results = list(self.evaluator.evaluate(uq, fact_base))

        self.assertEqual(len(results), 0)


class TestUnionQueryViaRegistry(unittest.TestCase):
    """Test UnionQuery evaluation via the registry."""

    def setUp(self):
        QueryEvaluatorRegistry.reset()
        self.registry = QueryEvaluatorRegistry.instance()

        self.p = Predicate("p", 1)
        self.x = Variable("X")
        self.a = Constant("a")
        self.b = Constant("b")

    def tearDown(self):
        QueryEvaluatorRegistry.reset()

    def test_get_evaluator_for_union_query(self):
        """Test that registry returns correct evaluator for UnionQuery."""
        foq = FOQuery(Atom(self.p, self.x), [self.x])
        uq = UnionQuery([foq], [self.x])

        evaluator = self.registry.get_evaluator(uq)

        self.assertIsNotNone(evaluator)
        self.assertIsInstance(evaluator, UnionQueryEvaluator)

    def test_evaluate_via_registry(self):
        """Test evaluating UnionQuery via the registry."""
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.p, self.b),
            ]
        )

        foq = FOQuery(Atom(self.p, self.x), [self.x])
        uq = UnionQuery([foq], [self.x])

        evaluator = self.registry.get_evaluator(uq)
        results = list(evaluator.evaluate(uq, fact_base))

        self.assertEqual(len(results), 2)


class TestUnionConjunctiveQueriesViaRegistry(unittest.TestCase):
    """Test UnionConjunctiveQueries evaluation via the registry (backward compatibility)."""

    def setUp(self):
        QueryEvaluatorRegistry.reset()
        self.registry = QueryEvaluatorRegistry.instance()

        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.a = Constant("a")
        self.b = Constant("b")

    def tearDown(self):
        QueryEvaluatorRegistry.reset()

    def test_get_evaluator_for_ucq(self):
        """Test that registry returns UnionQueryEvaluator for UnionConjunctiveQueries."""
        from prototyping_inference_engine.api.query.union_conjunctive_queries import (
            UnionConjunctiveQueries,
        )

        cq = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])
        ucq = UnionConjunctiveQueries([cq], [self.x])

        evaluator = self.registry.get_evaluator(ucq)

        self.assertIsNotNone(evaluator)
        self.assertIsInstance(evaluator, UnionQueryEvaluator)

    def test_evaluate_ucq_via_registry(self):
        """Test evaluating UnionConjunctiveQueries via the registry."""
        from prototyping_inference_engine.api.query.union_conjunctive_queries import (
            UnionConjunctiveQueries,
        )

        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.q, self.b),
            ]
        )

        cq1 = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])
        cq2 = ConjunctiveQuery(FrozenAtomSet([Atom(self.q, self.x)]), [self.x])
        ucq = UnionConjunctiveQueries([cq1, cq2], [self.x])

        evaluator = self.registry.get_evaluator(ucq)
        results = list(evaluator.evaluate(ucq, fact_base))

        self.assertEqual(len(results), 2)
        x_values = {r[self.x] for r in results}
        self.assertEqual(x_values, {self.a, self.b})


if __name__ == "__main__":
    unittest.main()
