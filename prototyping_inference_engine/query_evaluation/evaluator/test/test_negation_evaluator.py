"""
Tests for NegationFormulaEvaluator.
"""
import unittest
import warnings

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.query_evaluation.evaluator.negation_evaluator import (
    NegationFormulaEvaluator,
    UnsafeNegationWarning,
)
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import FormulaEvaluatorRegistry


class TestNegationFormulaEvaluator(unittest.TestCase):
    """Test NegationFormulaEvaluator."""

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
        self.evaluator = NegationFormulaEvaluator()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    def test_safe_negation_ground_true(self):
        """
        ¬p(c) where p(a), p(b) are facts.
        c is not in p, so negation succeeds.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.p, self.b),
        ])
        formula = NegationFormula(Atom(self.p, self.c))

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())

    def test_safe_negation_ground_false(self):
        """
        ¬p(a) where p(a) is a fact.
        Negation fails.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
        ])
        formula = NegationFormula(Atom(self.p, self.a))

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 0)

    def test_safe_negation_with_bound_variable_true(self):
        """
        ¬p(X) with X bound to c, where p(a), p(b) are facts.
        p(c) is not a fact, so negation succeeds.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.p, self.b),
        ])
        formula = NegationFormula(Atom(self.p, self.x))
        substitution = Substitution({self.x: self.c})

        results = list(self.evaluator.evaluate(formula, fact_base, substitution))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.c)

    def test_safe_negation_with_bound_variable_false(self):
        """
        ¬p(X) with X bound to a, where p(a) is a fact.
        Negation fails.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
        ])
        formula = NegationFormula(Atom(self.p, self.x))
        substitution = Substitution({self.x: self.a})

        results = list(self.evaluator.evaluate(formula, fact_base, substitution))

        self.assertEqual(len(results), 0)

    def test_unsafe_negation_emits_warning(self):
        """
        ¬p(X) with X free should emit UnsafeNegationWarning.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
        ])
        formula = NegationFormula(Atom(self.p, self.x))

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            list(self.evaluator.evaluate(formula, fact_base))
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, UnsafeNegationWarning))
            self.assertIn("X", str(w[0].message))

    def test_unsafe_negation_returns_complement(self):
        """
        ¬p(X) with X free.
        Domain = {a, b, c}, p = {a, b}
        Result should be {X→c}
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.p, self.b),
            Atom(self.q, self.c),  # c is in domain but not in p
        ])
        formula = NegationFormula(Atom(self.p, self.x))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UnsafeNegationWarning)
            results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.c)

    def test_unsafe_negation_multiple_results(self):
        """
        ¬p(X) with X free.
        Domain = {a, b, c, d}, p = {a}
        Result should be {X→b}, {X→c}, {X→d}
        """
        d = Constant("d")
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.q, self.b),
            Atom(self.q, self.c),
            Atom(self.q, d),
        ])
        formula = NegationFormula(Atom(self.p, self.x))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UnsafeNegationWarning)
            results = list(self.evaluator.evaluate(formula, fact_base))

        result_values = {r[self.x] for r in results}
        self.assertEqual(result_values, {self.b, self.c, d})

    def test_unsafe_negation_all_in_predicate(self):
        """
        ¬p(X) where domain = {a, b} and p = {a, b}
        Result should be empty.
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a),
            Atom(self.p, self.b),
        ])
        formula = NegationFormula(Atom(self.p, self.x))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UnsafeNegationWarning)
            results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 0)

    def test_unsafe_negation_none_in_predicate(self):
        """
        ¬p(X) where domain = {a, b} and p = {}
        Result should be {X→a}, {X→b}
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.q, self.a),
            Atom(self.q, self.b),
        ])
        formula = NegationFormula(Atom(self.p, self.x))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UnsafeNegationWarning)
            results = list(self.evaluator.evaluate(formula, fact_base))

        result_values = {r[self.x] for r in results}
        self.assertEqual(result_values, {self.a, self.b})

    def test_unsafe_negation_binary_predicate(self):
        """
        ¬r(X, Y) with both X and Y free.
        Domain = {a, b}, r = {(a, b)}
        Result should be all pairs except (a, b).
        """
        fact_base = MutableInMemoryFactBase([
            Atom(self.r, self.a, self.b),
        ])
        formula = NegationFormula(Atom(self.r, self.x, self.y))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UnsafeNegationWarning)
            results = list(self.evaluator.evaluate(formula, fact_base))

        result_pairs = {(r[self.x], r[self.y]) for r in results}
        # Domain = {a, b}, all pairs = {(a,a), (a,b), (b,a), (b,b)}
        # r = {(a,b)}, so complement = {(a,a), (b,a), (b,b)}
        expected = {(self.a, self.a), (self.b, self.a), (self.b, self.b)}
        self.assertEqual(result_pairs, expected)


class TestNegationInConjunction(unittest.TestCase):
    """Test negation within conjunction (safe pattern)."""

    def setUp(self):
        FormulaEvaluatorRegistry.reset()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    def test_safe_negation_in_conjunction(self):
        """
        q(X), ¬p(X) where q = {a, b, c} and p = {a}
        X is bound by q(X) before ¬p(X) is evaluated.
        Result: {X→b}, {X→c}
        """
        p = Predicate("p", 1)
        q = Predicate("q", 1)
        x = Variable("X")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        fact_base = MutableInMemoryFactBase([
            Atom(q, a),
            Atom(q, b),
            Atom(q, c),
            Atom(p, a),
        ])
        formula = ConjunctionFormula(
            Atom(q, x),
            NegationFormula(Atom(p, x)),
        )

        from prototyping_inference_engine.query_evaluation.evaluator.conjunction import (
            BacktrackConjunctionEvaluator,
        )
        evaluator = BacktrackConjunctionEvaluator()

        results = list(evaluator.evaluate(formula, fact_base))

        result_values = {r[x] for r in results}
        self.assertEqual(result_values, {b, c})

    def test_negation_filters_join(self):
        """
        r(X, Y), ¬p(Y) where r = {(a,b), (a,c)} and p = {b}
        Result: {X→a, Y→c}
        """
        p = Predicate("p", 1)
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
        ])
        formula = ConjunctionFormula(
            Atom(r, x, y),
            NegationFormula(Atom(p, y)),
        )

        from prototyping_inference_engine.query_evaluation.evaluator.conjunction import (
            BacktrackConjunctionEvaluator,
        )
        evaluator = BacktrackConjunctionEvaluator()

        results = list(evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][x], a)
        self.assertEqual(results[0][y], c)


if __name__ == "__main__":
    unittest.main()
