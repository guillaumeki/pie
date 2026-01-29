"""
Tests for FormulaBuilder.
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.formula import (
    NegationFormula,
    ConjunctionFormula,
    DisjunctionFormula,
    UniversalFormula,
    ExistentialFormula,
)
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestFormulaBuilder(unittest.TestCase):
    """Test FormulaBuilder fluent API."""

    def setUp(self):
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()

    def test_build_simple_atom(self):
        formula = self.session.formula().atom("p", "X", "Y").build()
        self.assertIsInstance(formula, Atom)
        self.assertEqual(str(formula), "p(X, Y)")

    def test_build_atom_with_constants(self):
        formula = self.session.formula().atom("p", "X", "a").build()
        self.assertIsInstance(formula, Atom)
        # X is uppercase (variable), a is lowercase (constant)
        self.assertEqual(len(formula.free_variables), 1)

    def test_build_negation(self):
        formula = self.session.formula().atom("p", "X").not_().build()
        self.assertIsInstance(formula, NegationFormula)
        self.assertEqual(str(formula), "¬(p(X))")

    def test_build_conjunction(self):
        formula = (
            self.session.formula()
            .atom("p", "X")
            .and_()
            .atom("q", "Y")
            .build()
        )
        self.assertIsInstance(formula, ConjunctionFormula)
        self.assertEqual(str(formula), "(p(X) ∧ q(Y))")

    def test_build_disjunction(self):
        formula = (
            self.session.formula()
            .atom("p", "X")
            .or_()
            .atom("q", "Y")
            .build()
        )
        self.assertIsInstance(formula, DisjunctionFormula)
        self.assertEqual(str(formula), "(p(X) ∨ q(Y))")

    def test_build_universal(self):
        formula = (
            self.session.formula()
            .forall("X")
            .atom("p", "X")
            .build()
        )
        self.assertIsInstance(formula, UniversalFormula)
        self.assertEqual(str(formula), "∀X.(p(X))")

    def test_build_existential(self):
        formula = (
            self.session.formula()
            .exists("X")
            .atom("p", "X")
            .build()
        )
        self.assertIsInstance(formula, ExistentialFormula)
        self.assertEqual(str(formula), "∃X.(p(X))")

    def test_build_nested_quantifiers(self):
        # ∀X.∃Y.p(X,Y)
        formula = (
            self.session.formula()
            .forall("X")
            .exists("Y")
            .atom("p", "X", "Y")
            .build()
        )
        self.assertIsInstance(formula, UniversalFormula)
        self.assertIsInstance(formula.inner, ExistentialFormula)
        self.assertTrue(formula.is_closed)
        self.assertEqual(str(formula), "∀X.(∃Y.(p(X, Y)))")

    def test_build_complex_formula(self):
        # ∀X.∃Y.(p(X,Y) ∧ q(Y))
        formula = (
            self.session.formula()
            .forall("X")
            .exists("Y")
            .atom("p", "X", "Y")
            .and_()
            .atom("q", "Y")
            .build()
        )
        self.assertIsInstance(formula, UniversalFormula)
        self.assertIsInstance(formula.inner, ExistentialFormula)
        self.assertIsInstance(formula.inner.inner, ConjunctionFormula)
        self.assertTrue(formula.is_closed)

    def test_build_conjunction_with_negation(self):
        # p(X) ∧ ¬q(Y)
        formula = (
            self.session.formula()
            .atom("p", "X")
            .and_()
            .atom("q", "Y")
            .not_()
            .build()
        )
        self.assertIsInstance(formula, ConjunctionFormula)
        self.assertIsInstance(formula.right, NegationFormula)

    def test_build_chained_conjunctions(self):
        # (p(X) ∧ q(Y)) ∧ r(Z)
        formula = (
            self.session.formula()
            .atom("p", "X")
            .and_()
            .atom("q", "Y")
            .and_()
            .atom("r", "Z")
            .build()
        )
        self.assertIsInstance(formula, ConjunctionFormula)
        self.assertIsInstance(formula.left, ConjunctionFormula)

    def test_build_chained_disjunctions(self):
        # (p(X) ∨ q(Y)) ∨ r(Z)
        formula = (
            self.session.formula()
            .atom("p", "X")
            .or_()
            .atom("q", "Y")
            .or_()
            .atom("r", "Z")
            .build()
        )
        self.assertIsInstance(formula, DisjunctionFormula)
        self.assertIsInstance(formula.left, DisjunctionFormula)

    def test_build_mixed_binary_operators(self):
        # (p(X) ∧ q(Y)) ∨ r(Z)
        formula = (
            self.session.formula()
            .atom("p", "X")
            .and_()
            .atom("q", "Y")
            .or_()
            .atom("r", "Z")
            .build()
        )
        self.assertIsInstance(formula, DisjunctionFormula)
        self.assertIsInstance(formula.left, ConjunctionFormula)

    def test_error_not_on_empty_stack(self):
        builder = self.session.formula()
        with self.assertRaises(ValueError):
            builder.not_()

    def test_error_and_requires_left_operand(self):
        builder = self.session.formula().and_()
        with self.assertRaises(ValueError):
            builder.build()

    def test_error_or_requires_left_operand(self):
        builder = self.session.formula().or_()
        with self.assertRaises(ValueError):
            builder.build()

    def test_formula_free_variables(self):
        formula = (
            self.session.formula()
            .forall("X")
            .atom("p", "X", "Y")
            .build()
        )
        self.assertEqual(len(formula.free_variables), 1)
        self.assertIn(self.session.variable("Y"), formula.free_variables)

    def test_formula_bound_variables(self):
        formula = (
            self.session.formula()
            .forall("X")
            .exists("Y")
            .atom("p", "X", "Y")
            .build()
        )
        self.assertEqual(len(formula.bound_variables), 2)
        self.assertIn(self.session.variable("X"), formula.bound_variables)
        self.assertIn(self.session.variable("Y"), formula.bound_variables)

    def test_formula_atoms(self):
        formula = (
            self.session.formula()
            .atom("p", "X")
            .and_()
            .atom("q", "Y")
            .build()
        )
        self.assertEqual(len(formula.atoms), 2)


class TestFormulaBuilderFromSession(unittest.TestCase):
    """Test FormulaBuilder via ReasoningSession.formula() method."""

    def test_session_formula_method(self):
        with ReasoningSession.create() as session:
            builder = session.formula()
            formula = builder.atom("p", "X").build()
            self.assertIsInstance(formula, Atom)

    def test_session_closed_raises_error(self):
        session = ReasoningSession.create()
        session.close()
        with self.assertRaises(RuntimeError):
            session.formula()


if __name__ == "__main__":
    unittest.main()
