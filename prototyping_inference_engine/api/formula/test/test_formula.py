"""
Tests for Formula classes.
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.api.formula import (
    Formula,
    NegationFormula,
    ConjunctionFormula,
    DisjunctionFormula,
    UniversalFormula,
    ExistentialFormula,
)


class TestAtomAsFormula(unittest.TestCase):
    """Test that Atom correctly implements the Formula interface."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.a = Constant("a")

    def test_atom_is_formula(self):
        atom = Atom(self.p, self.x, self.y)
        self.assertIsInstance(atom, Formula)

    def test_atom_free_variables(self):
        atom = Atom(self.p, self.x, self.y)
        self.assertEqual(atom.free_variables, frozenset([self.x, self.y]))

    def test_atom_bound_variables(self):
        atom = Atom(self.p, self.x, self.y)
        self.assertEqual(atom.bound_variables, frozenset())

    def test_atom_atoms(self):
        atom = Atom(self.p, self.x, self.y)
        self.assertEqual(atom.atoms, frozenset([atom]))

    def test_atom_is_ground_false(self):
        atom = Atom(self.p, self.x, self.y)
        self.assertFalse(atom.is_ground)

    def test_atom_is_ground_true(self):
        b = Constant("b")
        atom = Atom(self.p, self.a, b)
        self.assertTrue(atom.is_ground)


class TestNegationFormula(unittest.TestCase):
    """Test NegationFormula."""

    def setUp(self):
        self.p = Predicate("p", 1)
        self.x = Variable("X")
        self.y = Variable("Y")

    def test_negation_inner(self):
        atom = Atom(self.p, self.x)
        neg = NegationFormula(atom)
        self.assertEqual(neg.inner, atom)

    def test_negation_free_variables(self):
        atom = Atom(self.p, self.x)
        neg = NegationFormula(atom)
        self.assertEqual(neg.free_variables, frozenset([self.x]))

    def test_negation_bound_variables(self):
        atom = Atom(self.p, self.x)
        neg = NegationFormula(atom)
        self.assertEqual(neg.bound_variables, frozenset())

    def test_negation_atoms(self):
        atom = Atom(self.p, self.x)
        neg = NegationFormula(atom)
        self.assertEqual(neg.atoms, frozenset([atom]))

    def test_negation_substitution(self):
        atom = Atom(self.p, self.x)
        neg = NegationFormula(atom)
        sub = Substitution({self.x: self.y})
        result = neg.apply_substitution(sub)
        self.assertIsInstance(result, NegationFormula)
        self.assertEqual(result.inner, Atom(self.p, self.y))

    def test_negation_str(self):
        atom = Atom(self.p, self.x)
        neg = NegationFormula(atom)
        self.assertEqual(str(neg), "¬(p(X))")

    def test_negation_equality(self):
        atom = Atom(self.p, self.x)
        neg1 = NegationFormula(atom)
        neg2 = NegationFormula(atom)
        self.assertEqual(neg1, neg2)

    def test_negation_hash(self):
        atom = Atom(self.p, self.x)
        neg1 = NegationFormula(atom)
        neg2 = NegationFormula(atom)
        self.assertEqual(hash(neg1), hash(neg2))


class TestConjunctionFormula(unittest.TestCase):
    """Test ConjunctionFormula."""

    def setUp(self):
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")

    def test_conjunction_operands(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        conj = ConjunctionFormula(left, right)
        self.assertEqual(conj.left, left)
        self.assertEqual(conj.right, right)

    def test_conjunction_free_variables(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        conj = ConjunctionFormula(left, right)
        self.assertEqual(conj.free_variables, frozenset([self.x, self.y]))

    def test_conjunction_atoms(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        conj = ConjunctionFormula(left, right)
        self.assertEqual(conj.atoms, frozenset([left, right]))

    def test_conjunction_substitution(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        conj = ConjunctionFormula(left, right)
        z = Variable("Z")
        sub = Substitution({self.x: z})
        result = conj.apply_substitution(sub)
        self.assertIsInstance(result, ConjunctionFormula)
        self.assertEqual(result.left, Atom(self.p, z))
        self.assertEqual(result.right, Atom(self.q, self.y))

    def test_conjunction_str(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        conj = ConjunctionFormula(left, right)
        self.assertEqual(str(conj), "(p(X) ∧ q(Y))")

    def test_conjunction_symbol(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        conj = ConjunctionFormula(left, right)
        self.assertEqual(conj.symbol, "∧")


class TestDisjunctionFormula(unittest.TestCase):
    """Test DisjunctionFormula."""

    def setUp(self):
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")

    def test_disjunction_operands(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        disj = DisjunctionFormula(left, right)
        self.assertEqual(disj.left, left)
        self.assertEqual(disj.right, right)

    def test_disjunction_free_variables(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        disj = DisjunctionFormula(left, right)
        self.assertEqual(disj.free_variables, frozenset([self.x, self.y]))

    def test_disjunction_substitution(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        disj = DisjunctionFormula(left, right)
        z = Variable("Z")
        sub = Substitution({self.x: z})
        result = disj.apply_substitution(sub)
        self.assertIsInstance(result, DisjunctionFormula)
        self.assertEqual(result.left, Atom(self.p, z))

    def test_disjunction_str(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        disj = DisjunctionFormula(left, right)
        self.assertEqual(str(disj), "(p(X) ∨ q(Y))")

    def test_disjunction_symbol(self):
        left = Atom(self.p, self.x)
        right = Atom(self.q, self.y)
        disj = DisjunctionFormula(left, right)
        self.assertEqual(disj.symbol, "∨")


class TestUniversalFormula(unittest.TestCase):
    """Test UniversalFormula."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.x = Variable("X")
        self.y = Variable("Y")

    def test_universal_variable(self):
        atom = Atom(self.p, self.x, self.y)
        forall = UniversalFormula(self.x, atom)
        self.assertEqual(forall.variable, self.x)

    def test_universal_inner(self):
        atom = Atom(self.p, self.x, self.y)
        forall = UniversalFormula(self.x, atom)
        self.assertEqual(forall.inner, atom)

    def test_universal_free_variables(self):
        atom = Atom(self.p, self.x, self.y)
        forall = UniversalFormula(self.x, atom)
        self.assertEqual(forall.free_variables, frozenset([self.y]))

    def test_universal_bound_variables(self):
        atom = Atom(self.p, self.x, self.y)
        forall = UniversalFormula(self.x, atom)
        self.assertEqual(forall.bound_variables, frozenset([self.x]))

    def test_universal_is_closed(self):
        atom = Atom(self.p, self.x, self.y)
        forall_x = UniversalFormula(self.x, atom)
        forall_xy = UniversalFormula(self.y, forall_x)
        self.assertFalse(forall_x.is_closed)
        self.assertTrue(forall_xy.is_closed)

    def test_universal_substitution_free_var(self):
        atom = Atom(self.p, self.x, self.y)
        forall = UniversalFormula(self.x, atom)
        z = Variable("Z")
        sub = Substitution({self.y: z})
        result = forall.apply_substitution(sub)
        self.assertIsInstance(result, UniversalFormula)
        self.assertEqual(result.variable, self.x)
        self.assertEqual(result.inner, Atom(self.p, self.x, z))

    def test_universal_substitution_bound_var_ignored(self):
        atom = Atom(self.p, self.x, self.y)
        forall = UniversalFormula(self.x, atom)
        z = Variable("Z")
        sub = Substitution({self.x: z})  # Should be ignored (bound var)
        result = forall.apply_substitution(sub)
        self.assertEqual(result.variable, self.x)
        self.assertEqual(result.inner, atom)

    def test_universal_str(self):
        atom = Atom(self.p, self.x, self.y)
        forall = UniversalFormula(self.x, atom)
        self.assertEqual(str(forall), "∀X.(p(X, Y))")

    def test_universal_quantifier_symbol(self):
        atom = Atom(self.p, self.x, self.y)
        forall = UniversalFormula(self.x, atom)
        self.assertEqual(forall.quantifier_symbol, "∀")


class TestExistentialFormula(unittest.TestCase):
    """Test ExistentialFormula."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.x = Variable("X")
        self.y = Variable("Y")

    def test_existential_variable(self):
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.x, atom)
        self.assertEqual(exists.variable, self.x)

    def test_existential_inner(self):
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.x, atom)
        self.assertEqual(exists.inner, atom)

    def test_existential_free_variables(self):
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.x, atom)
        self.assertEqual(exists.free_variables, frozenset([self.y]))

    def test_existential_bound_variables(self):
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.x, atom)
        self.assertEqual(exists.bound_variables, frozenset([self.x]))

    def test_existential_str(self):
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.x, atom)
        self.assertEqual(str(exists), "∃X.(p(X, Y))")

    def test_existential_quantifier_symbol(self):
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.x, atom)
        self.assertEqual(exists.quantifier_symbol, "∃")


class TestNestedFormulas(unittest.TestCase):
    """Test nested formula combinations."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.z = Variable("Z")

    def test_nested_quantifiers(self):
        # ∀X.∃Y.p(X,Y)
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.y, atom)
        forall = UniversalFormula(self.x, exists)

        self.assertEqual(forall.free_variables, frozenset())
        self.assertEqual(forall.bound_variables, frozenset([self.x, self.y]))
        self.assertTrue(forall.is_closed)

    def test_complex_formula(self):
        # ∀X.(p(X,Y) ∧ ¬q(X))
        p_atom = Atom(self.p, self.x, self.y)
        q_atom = Atom(self.q, self.x)
        neg_q = NegationFormula(q_atom)
        conj = ConjunctionFormula(p_atom, neg_q)
        forall = UniversalFormula(self.x, conj)

        self.assertEqual(forall.free_variables, frozenset([self.y]))
        self.assertEqual(forall.bound_variables, frozenset([self.x]))
        self.assertFalse(forall.is_closed)
        self.assertEqual(forall.atoms, frozenset([p_atom, q_atom]))

    def test_nested_binary_formulas(self):
        # (p(X) ∧ q(Y)) ∨ p(Z)
        p_x = Atom(Predicate("p", 1), self.x)
        q_y = Atom(self.q, self.y)
        p_z = Atom(Predicate("p", 1), self.z)

        conj = ConjunctionFormula(p_x, q_y)
        disj = DisjunctionFormula(conj, p_z)

        self.assertEqual(disj.free_variables, frozenset([self.x, self.y, self.z]))
        self.assertEqual(disj.atoms, frozenset([p_x, q_y, p_z]))


if __name__ == "__main__":
    unittest.main()
