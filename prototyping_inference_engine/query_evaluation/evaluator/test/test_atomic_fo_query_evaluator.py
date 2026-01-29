"""
Tests for atomic FOQuery evaluation.

Based on test cases from Integraal's AtomicFOQueryEvaluatorTest.java:
https://gitlab.inria.fr/rules/integraal/-/blob/develop/integraal/integraal-query-evaluation/src/test/java/fr/boreal/test/query_evaluation/AtomicFOQueryEvaluatorTest.java
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.atom_evaluator import AtomEvaluator
from prototyping_inference_engine.query_evaluation.evaluator.fo_query_evaluator import FOQueryEvaluator
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import FormulaEvaluatorRegistry
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestAtomicFOQueryEvaluator(unittest.TestCase):
    """
    Test cases based on Integraal's AtomicFOQueryEvaluatorTest.

    Test fixtures:
    - factBase1: {p(a,a), p(a,b), p(c,d), p(x,x)} where x is a variable in facts
    - factBase2: {p(x,y)} where x,y are variables in facts
    - Predicates: p2 (arity 2)
    - Variables: x, y, z
    - Constants: a, b, c, d
    """

    @classmethod
    def setUpClass(cls):
        # Predicates
        cls.p2 = Predicate("p", 2)
        cls.q2 = Predicate("q", 2)

        # Variables (for queries)
        cls.x = Variable("X")
        cls.y = Variable("Y")
        cls.z = Variable("Z")

        # Constants
        cls.a = Constant("a")
        cls.b = Constant("b")
        cls.c = Constant("c")
        cls.d = Constant("d")

        # Fact bases
        # factBase1: {p(a,a), p(a,b), p(c,d)}
        # Note: In the original test, p(x,x) is also present where x is a constant-like
        # We'll use just constants for simplicity
        cls.fact_base_1 = MutableInMemoryFactBase([
            Atom(cls.p2, cls.a, cls.a),
            Atom(cls.p2, cls.a, cls.b),
            Atom(cls.p2, cls.c, cls.d),
        ])

        # factBase2: {p(a,b)} - a simple single fact
        cls.fact_base_2 = MutableInMemoryFactBase([
            Atom(cls.p2, cls.a, cls.b),
        ])

        # factBase3: empty
        cls.fact_base_3 = MutableInMemoryFactBase()

        # factBase4: {p(a,a), p(b,b), p(c,c)} - for reflexive queries
        cls.fact_base_4 = MutableInMemoryFactBase([
            Atom(cls.p2, cls.a, cls.a),
            Atom(cls.p2, cls.b, cls.b),
            Atom(cls.p2, cls.c, cls.c),
        ])

    def setUp(self):
        FormulaEvaluatorRegistry.reset()
        self.evaluator = FOQueryEvaluator()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    # =========================================================================
    # Test 1: Query p(X,X) against factBase2 {p(a,b)} - no match
    # =========================================================================
    def test_reflexive_query_no_match(self):
        """
        Query: ?() :- p(X,X)
        FactBase: {p(a,b)}
        Expected: no matches (a != b)
        """
        query = FOQuery(Atom(self.p2, self.x, self.x), [])
        results = list(self.evaluator.evaluate(query, self.fact_base_2))
        self.assertEqual(len(results), 0)

    # =========================================================================
    # Test 2: Query p(X,Y) against factBase1 with answer var [X]
    # =========================================================================
    def test_query_with_projection_on_first_var(self):
        """
        Query: ?(X) :- p(X,Y)
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: {a, c} (deduplicated since a appears twice)
        """
        query = FOQuery(Atom(self.p2, self.x, self.y), [self.x])
        results = list(self.evaluator.evaluate(query, self.fact_base_1))

        result_values = {r[0] for r in results}
        self.assertEqual(result_values, {self.a, self.c})

    # =========================================================================
    # Test 3: Query p(X,Y) against factBase1 with answer vars [X,Y]
    # =========================================================================
    def test_query_all_matches_no_projection(self):
        """
        Query: ?(X,Y) :- p(X,Y)
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: {(a,a), (a,b), (c,d)}
        """
        query = FOQuery(Atom(self.p2, self.x, self.y), [self.x, self.y])
        results = list(self.evaluator.evaluate(query, self.fact_base_1))

        result_set = set(results)
        expected = {
            (self.a, self.a),
            (self.a, self.b),
            (self.c, self.d),
        }
        self.assertEqual(result_set, expected)

    # =========================================================================
    # Test 4: Query with pre-homomorphism constraining X
    # =========================================================================
    def test_query_with_pre_substitution_on_first_var(self):
        """
        Query: ?(X) :- p(X,Y) with initial substitution {X -> a}
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: {a} (only matches where X=a)

        This tests the AtomEvaluator with an initial substitution.
        """
        atom_evaluator = AtomEvaluator()
        atom = Atom(self.p2, self.x, self.y)
        initial_sub = Substitution({self.x: self.a})

        results = list(atom_evaluator.evaluate(atom, self.fact_base_1, initial_sub))

        # All results should have X -> a
        for sub in results:
            self.assertEqual(sub[self.x], self.a)

        # Should match p(a,a) and p(a,b)
        self.assertEqual(len(results), 2)

    # =========================================================================
    # Test 5: Query with pre-homomorphism constraining Y
    # =========================================================================
    def test_query_with_pre_substitution_on_second_var(self):
        """
        Query: ?(X) :- p(X,Y) with initial substitution {Y -> d}
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: {c} (only p(c,d) matches)
        """
        atom_evaluator = AtomEvaluator()
        atom = Atom(self.p2, self.x, self.y)
        initial_sub = Substitution({self.y: self.d})

        results = list(atom_evaluator.evaluate(atom, self.fact_base_1, initial_sub))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.c)
        self.assertEqual(results[0][self.y], self.d)

    # =========================================================================
    # Test 6: Query with pre-homomorphism making it unsatisfiable
    # =========================================================================
    def test_query_with_conflicting_pre_substitution(self):
        """
        Query: ?(X) :- p(X,Y) with initial substitution {X -> a, Y -> d}
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: empty (no fact p(a,d))
        """
        atom_evaluator = AtomEvaluator()
        atom = Atom(self.p2, self.x, self.y)
        initial_sub = Substitution({self.x: self.a, self.y: self.d})

        results = list(atom_evaluator.evaluate(atom, self.fact_base_1, initial_sub))

        self.assertEqual(len(results), 0)

    # =========================================================================
    # Test 10: Boolean query that is true
    # =========================================================================
    def test_boolean_query_satisfied(self):
        """
        Query: ?() :- p(a,b)
        FactBase: {p(a,b)}
        Expected: one empty tuple (query is satisfied)
        """
        query = FOQuery(Atom(self.p2, self.a, self.b), [])
        results = list(self.evaluator.evaluate(query, self.fact_base_2))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ())

    # =========================================================================
    # Test 11: Boolean query that is false
    # =========================================================================
    def test_boolean_query_not_satisfied(self):
        """
        Query: ?() :- p(a,c)
        FactBase: {p(a,b)}
        Expected: empty (query not satisfied)
        """
        query = FOQuery(Atom(self.p2, self.a, self.c), [])
        results = list(self.evaluator.evaluate(query, self.fact_base_2))

        self.assertEqual(len(results), 0)

    # =========================================================================
    # Test 12: Query with missing predicate
    # =========================================================================
    def test_query_predicate_not_in_factbase(self):
        """
        Query: ?(X,Y) :- q(X,Y)
        FactBase: {p(a,b)} (no q facts)
        Expected: empty
        """
        query = FOQuery(Atom(self.q2, self.x, self.y), [self.x, self.y])
        results = list(self.evaluator.evaluate(query, self.fact_base_2))

        self.assertEqual(len(results), 0)

    # =========================================================================
    # Additional tests: reflexive queries
    # =========================================================================
    def test_reflexive_query_with_matches(self):
        """
        Query: ?(X) :- p(X,X)
        FactBase: {p(a,a), p(b,b), p(c,c)}
        Expected: {a, b, c}
        """
        query = FOQuery(Atom(self.p2, self.x, self.x), [self.x])
        results = list(self.evaluator.evaluate(query, self.fact_base_4))

        result_values = {r[0] for r in results}
        self.assertEqual(result_values, {self.a, self.b, self.c})

    def test_reflexive_query_partial_matches(self):
        """
        Query: ?(X) :- p(X,X)
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: {a} (only p(a,a) is reflexive)
        """
        query = FOQuery(Atom(self.p2, self.x, self.x), [self.x])
        results = list(self.evaluator.evaluate(query, self.fact_base_1))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (self.a,))

    # =========================================================================
    # Additional tests: empty fact base
    # =========================================================================
    def test_query_on_empty_factbase(self):
        """
        Query: ?(X,Y) :- p(X,Y)
        FactBase: {}
        Expected: empty
        """
        query = FOQuery(Atom(self.p2, self.x, self.y), [self.x, self.y])
        results = list(self.evaluator.evaluate(query, self.fact_base_3))

        self.assertEqual(len(results), 0)

    def test_boolean_query_on_empty_factbase(self):
        """
        Query: ?() :- p(a,b)
        FactBase: {}
        Expected: empty (not satisfied)
        """
        query = FOQuery(Atom(self.p2, self.a, self.b), [])
        results = list(self.evaluator.evaluate(query, self.fact_base_3))

        self.assertEqual(len(results), 0)

    # =========================================================================
    # Additional tests: multiple variables same value
    # =========================================================================
    def test_query_with_repeated_constant(self):
        """
        Query: ?(X) :- p(a,X)
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: {a, b}
        """
        query = FOQuery(Atom(self.p2, self.a, self.x), [self.x])
        results = list(self.evaluator.evaluate(query, self.fact_base_1))

        result_values = {r[0] for r in results}
        self.assertEqual(result_values, {self.a, self.b})

    def test_query_second_position_constant(self):
        """
        Query: ?(X) :- p(X,a)
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: {a} (only p(a,a) has 'a' in second position)
        """
        query = FOQuery(Atom(self.p2, self.x, self.a), [self.x])
        results = list(self.evaluator.evaluate(query, self.fact_base_1))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (self.a,))


if __name__ == "__main__":
    unittest.main()
