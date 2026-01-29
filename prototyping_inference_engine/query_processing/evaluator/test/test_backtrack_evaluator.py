"""
Tests for BacktrackConjunctionEvaluator.

Based on test cases from Integraal's BacktrackEvaluatorTest.java:
https://gitlab.inria.fr/rules/integraal/-/blob/develop/integraal/integraal-query-evaluation/src/test/java/fr/boreal/test/query_evaluation/BacktrackEvaluatorTest.java
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_processing.evaluator.conjunction.backtrack_conjunction_evaluator import (
    BacktrackConjunctionEvaluator,
)
from prototyping_inference_engine.query_processing.evaluator.fo_query_evaluator import FOQueryEvaluator
from prototyping_inference_engine.query_processing.evaluator.formula_evaluator_registry import FormulaEvaluatorRegistry
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestBacktrackEvaluatorIntegraal(unittest.TestCase):
    """
    Test cases based on Integraal's BacktrackEvaluatorTest.

    Fact bases:
    - factBase1: {p(a,a), p(a,b), p(c,d)}
    - factBase2: {p(a,b)}
    - factBase3: {p(a,b,c), p(b,c,d)} (arity 3)
    - fbPabPbc: {p(a,b), p(b,c)}
    - fbPabPcd: {p(a,b), p(c,d)}
    """

    @classmethod
    def setUpClass(cls):
        # Predicates
        cls.p2 = Predicate("p", 2)
        cls.p3 = Predicate("p3", 3)
        cls.q2 = Predicate("q", 2)

        # Variables
        cls.x = Variable("X")
        cls.y = Variable("Y")
        cls.z = Variable("Z")
        cls.w = Variable("W")
        cls.t = Variable("T")
        cls.u = Variable("U")

        # Constants
        cls.a = Constant("a")
        cls.b = Constant("b")
        cls.c = Constant("c")
        cls.d = Constant("d")

        # Fact bases
        cls.fact_base_1 = MutableInMemoryFactBase([
            Atom(cls.p2, cls.a, cls.a),
            Atom(cls.p2, cls.a, cls.b),
            Atom(cls.p2, cls.c, cls.d),
        ])

        cls.fact_base_2 = MutableInMemoryFactBase([
            Atom(cls.p2, cls.a, cls.b),
        ])

        cls.fact_base_3 = MutableInMemoryFactBase([
            Atom(cls.p3, cls.a, cls.b, cls.c),
            Atom(cls.p3, cls.b, cls.c, cls.d),
        ])

        # fbPabPbc: {p(a,b), p(b,c)} - joinable
        cls.fb_pab_pbc = MutableInMemoryFactBase([
            Atom(cls.p2, cls.a, cls.b),
            Atom(cls.p2, cls.b, cls.c),
        ])

        # fbPabPcd: {p(a,b), p(c,d)} - not joinable on Y=Z
        cls.fb_pab_pcd = MutableInMemoryFactBase([
            Atom(cls.p2, cls.a, cls.b),
            Atom(cls.p2, cls.c, cls.d),
        ])

    def setUp(self):
        FormulaEvaluatorRegistry.reset()
        self.evaluator = FOQueryEvaluator()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    # =========================================================================
    # Test from Integraal: query7 - Double predicate with join
    # p(X,Z,W) ∧ p(Z,W,T) with output {X}
    # =========================================================================
    def test_chain_join_arity3(self):
        """
        Query: ?(X) :- p3(X,Z,W) ∧ p3(Z,W,T)
        FactBase: {p3(a,b,c), p3(b,c,d)}
        Expected: {X→a} (chain: a->b->c->d)
        """
        formula = ConjunctionFormula(
            Atom(self.p3, self.x, self.z, self.w),
            Atom(self.p3, self.z, self.w, self.t),
        )
        query = FOQuery(formula, [self.x])

        results = list(self.evaluator.evaluate(query, self.fact_base_3))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (self.a,))

    def test_chain_join_full_output(self):
        """
        Query: ?(X,Z,W,T) :- p3(X,Z,W) ∧ p3(Z,W,T)
        FactBase: {p3(a,b,c), p3(b,c,d)}
        Expected: {X→a, Z→b, W→c, T→d}
        """
        formula = ConjunctionFormula(
            Atom(self.p3, self.x, self.z, self.w),
            Atom(self.p3, self.z, self.w, self.t),
        )
        query = FOQuery(formula, [self.x, self.z, self.w, self.t])

        results = list(self.evaluator.evaluate(query, self.fact_base_3))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (self.a, self.b, self.c, self.d))

    # =========================================================================
    # Tests: Double p with join - fbPabPbc
    # p(X,Y) ∧ p(Y,Z) - transitive pattern
    # =========================================================================
    def test_transitive_join_success(self):
        """
        Query: ?(X,Z) :- p(X,Y) ∧ p(Y,Z)
        FactBase: {p(a,b), p(b,c)}
        Expected: {X→a, Z→c} (path a->b->c)
        """
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.y, self.z),
        )
        query = FOQuery(formula, [self.x, self.z])

        results = list(self.evaluator.evaluate(query, self.fb_pab_pbc))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (self.a, self.c))

    def test_transitive_join_failure(self):
        """
        Query: ?(X,Z) :- p(X,Y) ∧ p(Y,Z)
        FactBase: {p(a,b), p(c,d)}
        Expected: empty (no join possible, b != c)
        """
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.y, self.z),
        )
        query = FOQuery(formula, [self.x, self.z])

        results = list(self.evaluator.evaluate(query, self.fb_pab_pcd))

        self.assertEqual(len(results), 0)

    def test_transitive_boolean_success(self):
        """
        Query: ?() :- p(X,Y) ∧ p(Y,Z)
        FactBase: {p(a,b), p(b,c)}
        Expected: true (one empty tuple)
        """
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.y, self.z),
        )
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate(query, self.fb_pab_pbc))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ())

    def test_transitive_boolean_failure(self):
        """
        Query: ?() :- p(X,Y) ∧ p(Y,Z)
        FactBase: {p(a,b), p(c,d)}
        Expected: false (empty)
        """
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.y, self.z),
        )
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate(query, self.fb_pab_pcd))

        self.assertEqual(len(results), 0)

    # =========================================================================
    # Tests: Cartesian product (no shared variables)
    # p(X,Y) ∧ p(Z,T) where Y != Z
    # =========================================================================
    def test_cartesian_product_small(self):
        """
        Query: ?(X,Z) :- p(X,Y) ∧ p(Z,T)
        FactBase: {p(a,b), p(b,c)}
        Expected: 4 results (2x2 cartesian)
        """
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.z, self.t),
        )
        query = FOQuery(formula, [self.x, self.z])

        results = list(self.evaluator.evaluate(query, self.fb_pab_pbc))

        self.assertEqual(len(results), 4)
        result_pairs = set(results)
        expected = {
            (self.a, self.a), (self.a, self.b),
            (self.b, self.a), (self.b, self.b),
        }
        self.assertEqual(result_pairs, expected)

    # =========================================================================
    # Tests: Self-join pattern
    # p(X,Y) ∧ p(X,Z) - same first argument
    # =========================================================================
    def test_self_join_same_first_arg(self):
        """
        Query: ?(X,Y,Z) :- p(X,Y) ∧ p(X,Z)
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: all pairs with same X
        """
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.x, self.z),
        )
        query = FOQuery(formula, [self.x, self.y, self.z])

        results = list(self.evaluator.evaluate(query, self.fact_base_1))

        # X=a: (a,a,a), (a,a,b), (a,b,a), (a,b,b) = 4
        # X=c: (c,d,d) = 1
        # Total: 5
        self.assertEqual(len(results), 5)

        x_values = {r[0] for r in results}
        self.assertEqual(x_values, {self.a, self.c})

    def test_self_join_projection(self):
        """
        Query: ?(X) :- p(X,Y) ∧ p(X,Z)
        FactBase: {p(a,a), p(a,b), p(c,d)}
        Expected: {a, c} (deduplicated)
        """
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.x, self.z),
        )
        query = FOQuery(formula, [self.x])

        results = list(self.evaluator.evaluate(query, self.fact_base_1))

        self.assertEqual(len(results), 2)
        result_values = {r[0] for r in results}
        self.assertEqual(result_values, {self.a, self.c})

    # =========================================================================
    # Tests: Triangle pattern (3-way join)
    # p(X,Y) ∧ p(Y,Z) ∧ p(Z,X)
    # =========================================================================
    def test_triangle_pattern(self):
        """
        Query: ?() :- p(X,Y) ∧ p(Y,Z) ∧ p(Z,X)
        FactBase: {p(a,b), p(b,c), p(c,a)}
        Expected: true (triangle a->b->c->a)
        """
        fb_triangle = MutableInMemoryFactBase([
            Atom(self.p2, self.a, self.b),
            Atom(self.p2, self.b, self.c),
            Atom(self.p2, self.c, self.a),
        ])
        inner = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.y, self.z),
        )
        formula = ConjunctionFormula(inner, Atom(self.p2, self.z, self.x))
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate(query, fb_triangle))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ())

    def test_triangle_no_match(self):
        """
        Query: ?() :- p(X,Y) ∧ p(Y,Z) ∧ p(Z,X)
        FactBase: {p(a,b), p(b,c), p(c,d)} (no cycle)
        Expected: false
        """
        fb_no_triangle = MutableInMemoryFactBase([
            Atom(self.p2, self.a, self.b),
            Atom(self.p2, self.b, self.c),
            Atom(self.p2, self.c, self.d),
        ])
        inner = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.y, self.z),
        )
        formula = ConjunctionFormula(inner, Atom(self.p2, self.z, self.x))
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate(query, fb_no_triangle))

        self.assertEqual(len(results), 0)

    # =========================================================================
    # Tests: Multiple predicates
    # p(X,Y) ∧ q(Y,Z)
    # =========================================================================
    def test_two_predicates_join(self):
        """
        Query: ?(X,Z) :- p(X,Y) ∧ q(Y,Z)
        FactBase: {p(a,b), q(b,c), q(b,d)}
        Expected: {(a,c), (a,d)}
        """
        fb = MutableInMemoryFactBase([
            Atom(self.p2, self.a, self.b),
            Atom(self.q2, self.b, self.c),
            Atom(self.q2, self.b, self.d),
        ])
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.q2, self.y, self.z),
        )
        query = FOQuery(formula, [self.x, self.z])

        results = list(self.evaluator.evaluate(query, fb))

        self.assertEqual(len(results), 2)
        result_pairs = set(results)
        self.assertEqual(result_pairs, {(self.a, self.c), (self.a, self.d)})

    def test_two_predicates_no_join(self):
        """
        Query: ?(X,Z) :- p(X,Y) ∧ q(Y,Z)
        FactBase: {p(a,b), q(c,d)} (no common value for Y)
        Expected: empty
        """
        fb = MutableInMemoryFactBase([
            Atom(self.p2, self.a, self.b),
            Atom(self.q2, self.c, self.d),
        ])
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.q2, self.y, self.z),
        )
        query = FOQuery(formula, [self.x, self.z])

        results = list(self.evaluator.evaluate(query, fb))

        self.assertEqual(len(results), 0)

    # =========================================================================
    # Tests: Long chain (4 atoms)
    # =========================================================================
    def test_long_chain(self):
        """
        Query: ?(A,E) :- p(A,B) ∧ p(B,C) ∧ p(C,D) ∧ p(D,E)
        FactBase: {p(1,2), p(2,3), p(3,4), p(4,5)}
        Expected: {(1,5)}
        """
        c1 = Constant("1")
        c2 = Constant("2")
        c3 = Constant("3")
        c4 = Constant("4")
        c5 = Constant("5")
        va = Variable("A")
        vb = Variable("B")
        vc = Variable("C")
        vd = Variable("D")
        ve = Variable("E")

        fb = MutableInMemoryFactBase([
            Atom(self.p2, c1, c2),
            Atom(self.p2, c2, c3),
            Atom(self.p2, c3, c4),
            Atom(self.p2, c4, c5),
        ])

        # Build: ((p(A,B) ∧ p(B,C)) ∧ p(C,D)) ∧ p(D,E)
        conj1 = ConjunctionFormula(Atom(self.p2, va, vb), Atom(self.p2, vb, vc))
        conj2 = ConjunctionFormula(conj1, Atom(self.p2, vc, vd))
        formula = ConjunctionFormula(conj2, Atom(self.p2, vd, ve))
        query = FOQuery(formula, [va, ve])

        results = list(self.evaluator.evaluate(query, fb))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (c1, c5))

    # =========================================================================
    # Tests: Pre-substitution with conjunction
    # =========================================================================
    def test_conjunction_with_pre_substitution(self):
        """
        Query: p(X,Y) ∧ p(Y,Z) with {Y→b}
        FactBase: {p(a,b), p(b,c), p(d,b)}
        Expected: {X→a, Z→c}, {X→d, Z→c}
        """
        fb = MutableInMemoryFactBase([
            Atom(self.p2, self.a, self.b),
            Atom(self.p2, self.b, self.c),
            Atom(self.p2, self.d, self.b),
        ])
        formula = ConjunctionFormula(
            Atom(self.p2, self.x, self.y),
            Atom(self.p2, self.y, self.z),
        )

        conj_evaluator = BacktrackConjunctionEvaluator()
        initial_sub = Substitution({self.y: self.b})
        results = list(conj_evaluator.evaluate(formula, fb, initial_sub))

        self.assertEqual(len(results), 2)
        x_values = {r[self.x] for r in results}
        self.assertEqual(x_values, {self.a, self.d})
        for r in results:
            self.assertEqual(r[self.y], self.b)
            self.assertEqual(r[self.z], self.c)


class TestBacktrackEvaluatorEdgeCases(unittest.TestCase):
    """Edge cases and special scenarios."""

    def setUp(self):
        FormulaEvaluatorRegistry.reset()
        self.evaluator = FOQueryEvaluator()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    def test_empty_fact_base(self):
        """Conjunction on empty fact base returns no results."""
        p = Predicate("p", 2)
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")

        fb = MutableInMemoryFactBase()
        formula = ConjunctionFormula(Atom(p, x, y), Atom(p, y, z))
        query = FOQuery(formula, [x, z])

        results = list(self.evaluator.evaluate(query, fb))

        self.assertEqual(len(results), 0)

    def test_single_fact_self_join(self):
        """
        Query: ?(X,Y,Z) :- p(X,Y) ∧ p(Y,Z)
        FactBase: {p(a,a)} (self-loop)
        Expected: {X→a, Y→a, Z→a}
        """
        p = Predicate("p", 2)
        a = Constant("a")
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")

        fb = MutableInMemoryFactBase([Atom(p, a, a)])
        formula = ConjunctionFormula(Atom(p, x, y), Atom(p, y, z))
        query = FOQuery(formula, [x, y, z])

        results = list(self.evaluator.evaluate(query, fb))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], (a, a, a))

    def test_conjunction_with_constants(self):
        """
        Query: ?() :- p(a,X) ∧ p(X,b)
        FactBase: {p(a,c), p(c,b)}
        Expected: true (X=c)
        """
        p = Predicate("p", 2)
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        x = Variable("X")

        fb = MutableInMemoryFactBase([Atom(p, a, c), Atom(p, c, b)])
        formula = ConjunctionFormula(Atom(p, a, x), Atom(p, x, b))
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate(query, fb))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ())

    def test_all_ground_conjunction_true(self):
        """
        Query: ?() :- p(a,b) ∧ p(b,c)
        FactBase: {p(a,b), p(b,c)}
        Expected: true
        """
        p = Predicate("p", 2)
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        fb = MutableInMemoryFactBase([Atom(p, a, b), Atom(p, b, c)])
        formula = ConjunctionFormula(Atom(p, a, b), Atom(p, b, c))
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate(query, fb))

        self.assertEqual(len(results), 1)

    def test_all_ground_conjunction_false(self):
        """
        Query: ?() :- p(a,b) ∧ p(b,d)
        FactBase: {p(a,b), p(b,c)}
        Expected: false (no p(b,d))
        """
        p = Predicate("p", 2)
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        d = Constant("d")

        fb = MutableInMemoryFactBase([Atom(p, a, b), Atom(p, b, c)])
        formula = ConjunctionFormula(Atom(p, a, b), Atom(p, b, d))
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate(query, fb))

        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
