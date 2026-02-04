"""
Tests for ExistentialFormulaEvaluator.
"""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.query_evaluation.evaluator.quantifiers.existential_formula_evaluator import (
    ExistentialFormulaEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.registry.formula_evaluator_registry import (
    FormulaEvaluatorRegistry,
)


class TestExistentialFormulaEvaluator(unittest.TestCase):
    """Test ExistentialFormulaEvaluator."""

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
        self.evaluator = ExistentialFormulaEvaluator()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    def test_existential_true_single_witness(self):
        """
        ∃x.p(x) where p = {a}.
        There exists x (namely a) such that p(x) holds.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
            ]
        )
        formula = ExistentialFormula(self.x, Atom(self.p, self.x))

        results = list(self.evaluator.evaluate(formula, fact_base))

        # ∃x.p(x) is true, returns empty substitution (x is bound)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())

    def test_existential_true_multiple_witnesses(self):
        """
        ∃x.p(x) where p = {a, b, c}.
        Multiple witnesses, but result is deduplicated to one.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.p, self.b),
                Atom(self.p, self.c),
            ]
        )
        formula = ExistentialFormula(self.x, Atom(self.p, self.x))

        results = list(self.evaluator.evaluate(formula, fact_base))

        # All witnesses project to same empty substitution
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())

    def test_existential_false_no_witness(self):
        """
        ∃x.p(x) where p = {}.
        No witness exists.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.q, self.a),  # Only q, not p
            ]
        )
        formula = ExistentialFormula(self.x, Atom(self.p, self.x))

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 0)

    def test_existential_with_free_var_projects_bound(self):
        """
        ∃x.r(x, Y) where r = {(a, b), (a, c), (b, b)}.
        For each Y, check if there exists an x such that r(x, Y).
        Y=b: x=a or x=b works → Y=b in result
        Y=c: x=a works → Y=c in result
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
                Atom(self.r, self.a, self.c),
                Atom(self.r, self.b, self.b),
            ]
        )
        formula = ExistentialFormula(self.x, Atom(self.r, self.x, self.y))

        results = list(self.evaluator.evaluate(formula, fact_base))

        # Y can be b or c
        result_values = {r[self.y] for r in results}
        self.assertEqual(result_values, {self.b, self.c})

    def test_existential_deduplicates_results(self):
        """
        ∃x.r(x, Y) where r = {(a, b), (c, b)}.
        Both witnesses give Y=b, should be deduplicated.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
                Atom(self.r, self.c, self.b),
            ]
        )
        formula = ExistentialFormula(self.x, Atom(self.r, self.x, self.y))

        results = list(self.evaluator.evaluate(formula, fact_base))

        # Only one result: Y=b (deduplicated)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.y], self.b)

    def test_existential_empty_fact_base(self):
        """
        ∃x.p(x) with empty fact base.
        No witnesses, false.
        """
        fact_base = MutableInMemoryFactBase([])
        formula = ExistentialFormula(self.x, Atom(self.p, self.x))

        results = list(self.evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 0)

    def test_existential_with_initial_substitution(self):
        """
        ∃x.r(x, Y) with Y already bound to b.
        r = {(a, b), (a, c)}.
        Should find x=a as witness for Y=b.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
                Atom(self.r, self.a, self.c),
            ]
        )
        formula = ExistentialFormula(self.x, Atom(self.r, self.x, self.y))
        initial_sub = Substitution({self.y: self.b})

        results = list(self.evaluator.evaluate(formula, fact_base, initial_sub))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.y], self.b)

    def test_existential_with_initial_substitution_no_match(self):
        """
        ∃x.r(x, Y) with Y bound to c.
        r = {(a, b)}.
        No r(_, c), so no witness.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
            ]
        )
        formula = ExistentialFormula(self.x, Atom(self.r, self.x, self.y))
        initial_sub = Substitution({self.y: self.c})

        results = list(self.evaluator.evaluate(formula, fact_base, initial_sub))

        self.assertEqual(len(results), 0)

    def test_nested_existential(self):
        """
        ∃x.∃y.r(x, y) where r = {(a, b)}.
        Both x and y are bound and projected out.
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.r, self.a, self.b),
            ]
        )
        inner = ExistentialFormula(self.y, Atom(self.r, self.x, self.y))
        formula = ExistentialFormula(self.x, inner)

        results = list(self.evaluator.evaluate(formula, fact_base))

        # Both variables projected out, result is empty substitution
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())


class TestExistentialInConjunction(unittest.TestCase):
    """Test existential quantifier within conjunction."""

    def setUp(self):
        FormulaEvaluatorRegistry.reset()

    def tearDown(self):
        FormulaEvaluatorRegistry.reset()

    def test_existential_in_conjunction(self):
        """
        p(Y), ∃x.r(x, Y)
        p = {a, b, c}, r = {(d, a), (d, b)}.
        Y bound by p, then ∃x.r(x, Y) checked.
        For Y=a: r(d, a) exists → success
        For Y=b: r(d, b) exists → success
        For Y=c: no r(_, c) → fail
        Result: {Y→a}, {Y→b}
        """
        p = Predicate("p", 1)
        r = Predicate("r", 2)
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        d = Constant("d")

        fact_base = MutableInMemoryFactBase(
            [
                Atom(p, a),
                Atom(p, b),
                Atom(p, c),
                Atom(r, d, a),
                Atom(r, d, b),
            ]
        )
        formula = ConjunctionFormula(
            Atom(p, y),
            ExistentialFormula(x, Atom(r, x, y)),
        )

        from prototyping_inference_engine.query_evaluation.evaluator.conjunction import (
            BacktrackConjunctionEvaluator,
        )

        evaluator = BacktrackConjunctionEvaluator()

        results = list(evaluator.evaluate(formula, fact_base))

        self.assertEqual(len(results), 2)
        result_values = {r[y] for r in results}
        self.assertEqual(result_values, {a, b})

    def test_existential_join(self):
        """
        ∃x.(p(x) ∧ q(x))
        p = {a, b}, q = {b, c}.
        Intersection: only x=b satisfies both.
        """
        p = Predicate("p", 1)
        q = Predicate("q", 1)
        x = Variable("X")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        fact_base = MutableInMemoryFactBase(
            [
                Atom(p, a),
                Atom(p, b),
                Atom(q, b),
                Atom(q, c),
            ]
        )
        inner = ConjunctionFormula(Atom(p, x), Atom(q, x))
        formula = ExistentialFormula(x, inner)

        evaluator = ExistentialFormulaEvaluator()
        results = list(evaluator.evaluate(formula, fact_base))

        # x=b is the only witness, projected out
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], Substitution())


if __name__ == "__main__":
    unittest.main()
