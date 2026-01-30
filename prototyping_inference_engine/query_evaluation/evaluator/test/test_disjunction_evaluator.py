"""
Tests for DisjunctionFormulaEvaluator.
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.api.formula.disjunction_formula import DisjunctionFormula
from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.query_evaluation.evaluator.disjunction_evaluator import (
    DisjunctionFormulaEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import FormulaEvaluatorRegistry


class TestDisjunctionFormulaEvaluator(unittest.TestCase):
    """Test DisjunctionFormulaEvaluator."""

    @classmethod
    def setUpClass(cls):
        cls.p = Predicate("p", 1)
        cls.q = Predicate("q", 1)
        cls.r = Predicate("r", 2)

        cls.x = Variable("X")
        cls.y = Variable("Y")

        cls.a = Constant("a")
        cls.b = Constant("b")
        cls.c = Constant("c")

    def setUp(self):
        FormulaEvaluatorRegistry.reset()
        self.evaluator = DisjunctionFormulaEvaluator()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    def test_disjunction_left_only(self):
        """
        p(X) ∨ q(X) where p = {a} and q = {}.
        Only left side has results.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.x),
            Atom(self.q, self.x),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)

    def test_disjunction_right_only(self):
        """
        p(X) ∨ q(X) where p = {} and q = {b}.
        Only right side has results.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.q, self.b),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.x),
            Atom(self.q, self.x),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.b)

    def test_disjunction_both_sides(self):
        """
        p(X) ∨ q(X) where p = {a} and q = {b}.
        Both sides have results, union returned.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.q, self.b),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.x),
            Atom(self.q, self.x),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 2)
        result_values = {r[self.x] for r in results}
        self.assertEqual(result_values, {self.a, self.b})

    def test_disjunction_neither_side(self):
        """
        p(X) ∨ q(X) where p = {} and q = {}.
        Neither side has results.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.r, self.a, self.b),  # Different predicate
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.x),
            Atom(self.q, self.x),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 0)

    def test_disjunction_deduplicates(self):
        """
        p(X) ∨ q(X) where p = {a} and q = {a}.
        Same result from both sides, deduplicated.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.q, self.a),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.x),
            Atom(self.q, self.x),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        # Should be deduplicated to one result
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)

    def test_disjunction_partial_overlap(self):
        """
        p(X) ∨ q(X) where p = {a, b} and q = {b, c}.
        Overlap at b, should be deduplicated.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.p, self.b),
            Atom(self.q, self.b),
            Atom(self.q, self.c),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.x),
            Atom(self.q, self.x),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        # a, b, c but b only once
        self.assertEqual(len(results), 3)
        result_values = {r[self.x] for r in results}
        self.assertEqual(result_values, {self.a, self.b, self.c})

    def test_disjunction_ground_left_true(self):
        """
        p(a) ∨ q(b) where p = {a}.
        Left side is true.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.a),
            Atom(self.q, self.b),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())

    def test_disjunction_ground_right_true(self):
        """
        p(a) ∨ q(b) where q = {b}.
        Right side is true.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.q, self.b),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.a),
            Atom(self.q, self.b),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())

    def test_disjunction_ground_both_true(self):
        """
        p(a) ∨ q(b) where p = {a} and q = {b}.
        Both sides are true, deduplicated to one.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.q, self.b),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.a),
            Atom(self.q, self.b),
        )

        results = list(self.evaluator.evaluate(formula, fact_base))

        # Both yield empty substitution, deduplicated
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())

    def test_disjunction_with_initial_substitution(self):
        """
        p(X) ∨ q(X) with X bound to a, where p = {a, b} and q = {c}.
        Only p(a) matches.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.p, self.b),
            Atom(self.q, self.c),
        ])
        formula = DisjunctionFormula(
            Atom(self.p, self.x),
            Atom(self.q, self.x),
        )
        initial_sub = Substitution({self.x: self.a})

        results = list(self.evaluator.evaluate(formula, fact_base, initial_sub))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)

    def test_nested_disjunction(self):
        """
        (p(X) ∨ q(X)) ∨ r(X, Y)
        where p = {a}, q = {b}, r = {(c, d)}.
        """
        d = Constant("d")
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.q, self.b),
            Atom(self.r, self.c, d),
        ])
        inner = DisjunctionFormula(
            Atom(self.p, self.x),
            Atom(self.q, self.x),
        )
        formula = DisjunctionFormula(inner, Atom(self.r, self.x, self.y))

        results = list(self.evaluator.evaluate(formula, fact_base))

        # X=a (from p), X=b (from q), X=c,Y=d (from r)
        self.assertEqual(len(results), 3)


class TestDisjunctionInConjunction(unittest.TestCase):
    """Test disjunction within conjunction."""

    def setUp(self):
        FormulaEvaluatorRegistry.reset()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    def test_disjunction_in_conjunction(self):
        """
        r(X, Y) ∧ (p(Y) ∨ q(Y))
        r = {(a, b), (a, c)}, p = {b}, q = {c}.
        For (a, b): p(b) is true → success
        For (a, c): q(c) is true → success
        """
        p = Predicate("p", 1)
        q = Predicate("q", 1)
        r = Predicate("r", 2)
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        fact_base = MutableInMemoryFactBase([
            Atom(r, a, b),
            Atom(r, a, c),
            Atom(p, b),
            Atom(q, c),
        ])
        disj = DisjunctionFormula(Atom(p, y), Atom(q, y))
        formula = ConjunctionFormula(Atom(r, x, y), disj)

        from prototyping_inference_engine.query_evaluation.evaluator.conjunction import (
            BacktrackConjunctionEvaluator,
        )
        evaluator = BacktrackConjunctionEvaluator()

        results = list(evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 2)
        result_pairs = {(r[x], r[y]) for r in results}
        self.assertEqual(result_pairs, {(a, b), (a, c)})


if __name__ == "__main__":
    unittest.main()
