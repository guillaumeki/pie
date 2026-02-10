"""
Tests for universal evaluation via FOQuery evaluators.
"""

import unittest
import warnings

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.warnings import (
    UniversalQuantifierWarning,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
)


def _evaluate_formula(evaluator, formula, data, substitution=None):
    query = FOQuery(formula, sorted(formula.free_variables, key=lambda v: str(v)))
    return list(evaluator.evaluate(query, data, substitution))


class TestUniversalEvaluation(unittest.TestCase):
    """Test universal evaluation via FOQuery evaluators."""

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
        self.evaluator = GenericFOQueryEvaluator()

    def test_universal_emits_warning(self):
        """∀x.p(x) should emit UniversalQuantifierWarning."""
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
            ]
        )
        formula = UniversalFormula(self.x, Atom(self.p, self.x))

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _evaluate_formula(self.evaluator, formula, fact_base)
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, UniversalQuantifierWarning))

    def test_universal_true_all_in_predicate(self):
        """
        ∀x.p(x) where domain = {a, b} and p = {a, b}.
        All domain elements satisfy p, so ∀ is true.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.p, self.b),
            ]
        )
        formula = UniversalFormula(self.x, Atom(self.p, self.x))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())

    def test_universal_false_not_all_in_predicate(self):
        """
        ∀x.p(x) where domain = {a, b, c} and p = {a, b}.
        c is not in p, so ∀ is false.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.p, self.b),
                Atom(self.q, self.c),  # c is in domain but not in p
            ]
        )
        formula = UniversalFormula(self.x, Atom(self.p, self.x))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 0)

    def test_universal_empty_domain(self):
        """
        ∀x.p(x) with empty domain.
        Vacuously true.
        """
        fact_base = MutableInMemoryFactBase([])
        formula = UniversalFormula(self.x, Atom(self.p, self.x))

        # Empty domain doesn't trigger warning
        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())

    def test_universal_single_element_domain_true(self):
        """
        ∀x.p(x) where domain = {a} and p = {a}.
        True.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
            ]
        )
        formula = UniversalFormula(self.x, Atom(self.p, self.x))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)

    def test_universal_single_element_domain_false(self):
        """
        ∀x.p(x) where domain = {a} and p = {}.
        False.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.q, self.a),  # a is in domain but not in p
            ]
        )
        formula = UniversalFormula(self.x, Atom(self.p, self.x))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 0)

    def test_universal_with_free_var_intersection(self):
        """
        ∀x.r(x, Y) where r = {(a, b), (a, c), (b, b)}.
        Domain = {a, b, c}.
        For x=a: Y ∈ {b, c}
        For x=b: Y ∈ {b}
        For x=c: no Y
        Intersection is empty, so no result.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
                Atom(self.r, self.a, self.c),
                Atom(self.r, self.b, self.b),
            ]
        )
        formula = UniversalFormula(self.x, Atom(self.r, self.x, self.y))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base)

        # c has no r(c, Y), so intersection is empty
        self.assertEqual(len(results), 0)

    def test_universal_with_free_var_success(self):
        """
        ∀x.r(x, Y) where r = {(a, b), (b, b)}.
        Domain = {a, b}.
        For x=a: Y ∈ {b}
        For x=b: Y ∈ {b}
        Intersection: Y = b.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
                Atom(self.r, self.b, self.b),
            ]
        )
        formula = UniversalFormula(self.x, Atom(self.r, self.x, self.y))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.y], self.b)

    def test_universal_with_free_var_multiple_results(self):
        """
        ∀x.r(x, Y) where r = {(a, b), (a, c), (b, b), (b, c)}.
        Domain = {a, b, c} (all terms appearing in facts).
        For x=a: Y ∈ {b, c}
        For x=b: Y ∈ {b, c}
        For x=c: Y ∈ {} (no r(c, _))
        Intersection is empty.

        To get multiple results, we need r to cover all domain elements.
        """
        # Use a setup where domain = {a, b} exactly
        # Better test: domain = {a, b} with r covering both
        r2 = Predicate("r2", 2)
        fact_base2 = MutableInMemoryFactBase(
            [
                Atom(r2, self.a, self.a),
                Atom(r2, self.a, self.b),
                Atom(r2, self.b, self.a),
                Atom(r2, self.b, self.b),
            ]
        )
        # Domain = {a, b}
        # For x=a: Y ∈ {a, b}
        # For x=b: Y ∈ {a, b}
        # Intersection: {a, b}
        formula = UniversalFormula(self.x, Atom(r2, self.x, self.y))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base2)

        result_values = {r[self.y] for r in results}
        self.assertEqual(result_values, {self.a, self.b})

    def test_universal_with_initial_substitution(self):
        """
        ∀x.r(x, Y) with Y already bound to b.
        r = {(a, b), (b, b)}, domain = {a, b}.
        Should succeed since r(a, b) and r(b, b) both exist.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
                Atom(self.r, self.b, self.b),
            ]
        )
        formula = UniversalFormula(self.x, Atom(self.r, self.x, self.y))
        initial_sub = Substitution({self.y: self.b})

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base, initial_sub)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.y], self.b)


class TestUniversalInConjunction(unittest.TestCase):
    """Test universal quantifier within conjunction."""

    def setUp(self):
        self.evaluator = GenericFOQueryEvaluator()

    def test_universal_after_binding(self):
        """
        q(Y), ∀x.r(x, Y)
        q = {a, b}, r = {(a, a), (a, b), (b, a), (b, b)}, domain = {a, b}.
        Y bound by q first, then ∀x.r(x, Y) checked.
        For Y=a: r(a, a) and r(b, a) exist → success
        For Y=b: r(a, b) and r(b, b) exist → success
        Result: {Y→a}, {Y→b}
        """
        q = Predicate("q", 1)
        r = Predicate("r", 2)
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")

        fact_base = MutableInMemoryFactBase(
            [
                Atom(q, a),
                Atom(q, b),
                Atom(r, a, a),
                Atom(r, a, b),
                Atom(r, b, a),
                Atom(r, b, b),
            ]
        )
        formula = ConjunctionFormula(
            Atom(q, y),
            UniversalFormula(x, Atom(r, x, y)),
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UniversalQuantifierWarning)
            results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 2)
        result_values = {r[y] for r in results}
        self.assertEqual(result_values, {a, b})


if __name__ == "__main__":
    unittest.main()
