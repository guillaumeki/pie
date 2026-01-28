from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.atom_operations import specialize
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestSpecialize(TestCase):
    def test_identical_ground_atoms(self):
        """Test specializing identical ground atoms returns empty substitution."""
        p = Predicate("p", 2)
        atom = Atom(p, Constant("a"), Constant("b"))
        result = specialize(atom, atom)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_variable_to_constant(self):
        """Test specializing variable to constant."""
        p = Predicate("p", 1)
        from_atom = Atom(p, Variable("X"))
        to_atom = Atom(p, Constant("a"))
        result = specialize(from_atom, to_atom)
        self.assertIsNotNone(result)
        self.assertEqual(result[Variable("X")], Constant("a"))

    def test_variable_to_variable(self):
        """Test specializing variable to another variable."""
        p = Predicate("p", 1)
        from_atom = Atom(p, Variable("X"))
        to_atom = Atom(p, Variable("Y"))
        result = specialize(from_atom, to_atom)
        self.assertIsNotNone(result)
        self.assertEqual(result[Variable("X")], Variable("Y"))

    def test_multiple_variables(self):
        """Test specializing multiple variables."""
        p = Predicate("p", 2)
        from_atom = Atom(p, Variable("X"), Variable("Y"))
        to_atom = Atom(p, Constant("a"), Constant("b"))
        result = specialize(from_atom, to_atom)
        self.assertIsNotNone(result)
        self.assertEqual(result[Variable("X")], Constant("a"))
        self.assertEqual(result[Variable("Y")], Constant("b"))

    def test_same_variable_multiple_times(self):
        """Test specializing same variable appearing multiple times."""
        p = Predicate("p", 2)
        from_atom = Atom(p, Variable("X"), Variable("X"))
        to_atom = Atom(p, Constant("a"), Constant("a"))
        result = specialize(from_atom, to_atom)
        self.assertIsNotNone(result)
        self.assertEqual(result[Variable("X")], Constant("a"))

    def test_same_variable_conflicting_values(self):
        """Test specializing same variable to different values fails."""
        p = Predicate("p", 2)
        from_atom = Atom(p, Variable("X"), Variable("X"))
        to_atom = Atom(p, Constant("a"), Constant("b"))
        result = specialize(from_atom, to_atom)
        self.assertIsNone(result)

    def test_different_predicates(self):
        """Test specializing atoms with different predicates fails."""
        p1 = Predicate("p", 1)
        p2 = Predicate("q", 1)
        from_atom = Atom(p1, Variable("X"))
        to_atom = Atom(p2, Constant("a"))
        result = specialize(from_atom, to_atom)
        self.assertIsNone(result)

    def test_constant_mismatch(self):
        """Test specializing with mismatched constants fails."""
        p = Predicate("p", 1)
        from_atom = Atom(p, Constant("a"))
        to_atom = Atom(p, Constant("b"))
        result = specialize(from_atom, to_atom)
        self.assertIsNone(result)

    def test_constant_to_variable(self):
        """Test that constant in from_atom must match exact term in to_atom."""
        p = Predicate("p", 1)
        from_atom = Atom(p, Constant("a"))
        to_atom = Atom(p, Variable("X"))
        result = specialize(from_atom, to_atom)
        # Constant "a" != Variable "X", so specialization fails
        self.assertIsNone(result)

    def test_with_initial_substitution(self):
        """Test specializing with initial substitution."""
        p = Predicate("p", 2)
        x = Variable("X")
        y = Variable("Y")
        from_atom = Atom(p, x, y)
        to_atom = Atom(p, Constant("a"), Constant("b"))

        # Initial substitution already maps X -> a
        initial_sub = Substitution({x: Constant("a")})
        result = specialize(from_atom, to_atom, initial_sub)
        self.assertIsNotNone(result)
        self.assertEqual(result[x], Constant("a"))
        self.assertEqual(result[y], Constant("b"))

    def test_with_conflicting_initial_substitution(self):
        """Test specializing with conflicting initial substitution fails."""
        p = Predicate("p", 1)
        x = Variable("X")
        from_atom = Atom(p, x)
        to_atom = Atom(p, Constant("b"))

        # Initial substitution maps X -> a, but to_atom needs X -> b
        initial_sub = Substitution({x: Constant("a")})
        result = specialize(from_atom, to_atom, initial_sub)
        self.assertIsNone(result)

    def test_mixed_constants_and_variables(self):
        """Test specializing with mix of constants and variables."""
        p = Predicate("p", 3)
        from_atom = Atom(p, Variable("X"), Constant("a"), Variable("Y"))
        to_atom = Atom(p, Constant("b"), Constant("a"), Constant("c"))
        result = specialize(from_atom, to_atom)
        self.assertIsNotNone(result)
        self.assertEqual(result[Variable("X")], Constant("b"))
        self.assertEqual(result[Variable("Y")], Constant("c"))

    def test_mixed_fail_on_constant_mismatch(self):
        """Test that constant mismatch fails even with variables present."""
        p = Predicate("p", 2)
        from_atom = Atom(p, Constant("a"), Variable("X"))
        to_atom = Atom(p, Constant("b"), Constant("c"))
        result = specialize(from_atom, to_atom)
        self.assertIsNone(result)

    def test_zero_arity(self):
        """Test specializing zero-arity atoms."""
        p = Predicate("prop", 0)
        from_atom = Atom(p)
        to_atom = Atom(p)
        result = specialize(from_atom, to_atom)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)
