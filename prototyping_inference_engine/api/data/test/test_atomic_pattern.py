"""Tests for atomic patterns."""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.atomic_pattern import (
    AtomicPattern,
    UnconstrainedPattern,
    SimpleAtomicPattern,
)
from prototyping_inference_engine.api.data.constraint import CONSTANT, GROUND
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestUnconstrainedPattern(unittest.TestCase):
    """Test UnconstrainedPattern."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.pattern = UnconstrainedPattern(self.p)

    def test_predicate(self):
        """Test predicate property."""
        self.assertEqual(self.pattern.predicate, self.p)

    def test_get_constraint_returns_none(self):
        """All positions are unconstrained."""
        self.assertIsNone(self.pattern.get_constraint(0))
        self.assertIsNone(self.pattern.get_constraint(1))
        self.assertIsNone(self.pattern.get_constraint(99))

    def test_can_evaluate_matching_predicate(self):
        """Any atom with matching predicate can be evaluated."""
        atom = Atom(self.p, Variable("X"), Variable("Y"))
        self.assertTrue(self.pattern.can_evaluate_with(atom))

    def test_cannot_evaluate_different_predicate(self):
        """Atom with different predicate cannot be evaluated."""
        atom = Atom(self.q, Variable("X"))
        self.assertFalse(self.pattern.can_evaluate_with(atom))

    def test_repr(self):
        """Test repr."""
        self.assertIn("UnconstrainedPattern", repr(self.pattern))


class TestSimpleAtomicPattern(unittest.TestCase):
    """Test SimpleAtomicPattern."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.a = Constant("a")
        self.b = Constant("b")

    def test_no_constraints(self):
        """Pattern with no constraints accepts any terms."""
        pattern = SimpleAtomicPattern(self.p)
        atom = Atom(self.p, self.x, self.y)
        self.assertTrue(pattern.can_evaluate_with(atom))

    def test_constant_constraint_satisfied(self):
        """Constant constraint satisfied by constant."""
        pattern = SimpleAtomicPattern(self.p, {0: CONSTANT})
        atom = Atom(self.p, self.a, self.y)
        self.assertTrue(pattern.can_evaluate_with(atom))

    def test_constant_constraint_not_satisfied(self):
        """Constant constraint not satisfied by variable."""
        pattern = SimpleAtomicPattern(self.p, {0: CONSTANT})
        atom = Atom(self.p, self.x, self.y)
        self.assertFalse(pattern.can_evaluate_with(atom))

    def test_constraint_with_substitution(self):
        """Constraint checked after applying substitution."""
        pattern = SimpleAtomicPattern(self.p, {0: CONSTANT})
        atom = Atom(self.p, self.x, self.y)

        # Without substitution: X is variable, fails
        self.assertFalse(pattern.can_evaluate_with(atom))

        # With substitution {X -> a}: X resolves to constant, succeeds
        sub = Substitution({self.x: self.a})
        self.assertTrue(pattern.can_evaluate_with(atom, sub))

    def test_multiple_constraints(self):
        """Multiple position constraints."""
        pattern = SimpleAtomicPattern(self.p, {0: CONSTANT, 1: GROUND})

        # Both satisfied
        atom1 = Atom(self.p, self.a, self.b)
        self.assertTrue(pattern.can_evaluate_with(atom1))

        # First satisfied, second not
        atom2 = Atom(self.p, self.a, self.y)
        self.assertFalse(pattern.can_evaluate_with(atom2))

    def test_constrained_positions(self):
        """Test constrained_positions property."""
        pattern = SimpleAtomicPattern(self.p, {0: CONSTANT, 1: GROUND})
        self.assertEqual(pattern.constrained_positions, frozenset({0, 1}))

    def test_get_unsatisfied_positions(self):
        """Test get_unsatisfied_positions method."""
        pattern = SimpleAtomicPattern(self.p, {0: CONSTANT, 1: GROUND})
        atom = Atom(self.p, self.x, self.y)

        unsatisfied = pattern.get_unsatisfied_positions(atom)

        self.assertEqual(set(unsatisfied.keys()), {0, 1})
        self.assertEqual(unsatisfied[0], CONSTANT)
        self.assertEqual(unsatisfied[1], GROUND)

    def test_get_unsatisfied_positions_with_substitution(self):
        """Test get_unsatisfied_positions with substitution."""
        pattern = SimpleAtomicPattern(self.p, {0: CONSTANT, 1: GROUND})
        atom = Atom(self.p, self.x, self.y)
        sub = Substitution({self.x: self.a})  # X -> a

        unsatisfied = pattern.get_unsatisfied_positions(atom, sub)

        # Position 0 now satisfied (X -> a), only position 1 unsatisfied
        self.assertEqual(set(unsatisfied.keys()), {1})

    def test_repr_with_constraints(self):
        """Test repr with constraints."""
        pattern = SimpleAtomicPattern(self.p, {0: CONSTANT})
        r = repr(pattern)
        self.assertIn("SimpleAtomicPattern", r)
        self.assertIn("constant", r)


class TestAtomicPatternAPI(unittest.TestCase):
    """Test AtomicPattern use case: API with mandatory ID."""

    def test_api_pattern(self):
        """Simulate API endpoint requiring an ID at position 0."""
        # Predicate: user(id, name)
        user = Predicate("user", 2)

        # API requires id (position 0) to be a constant
        pattern = SimpleAtomicPattern(user, {0: CONSTANT})

        x = Variable("X")
        y = Variable("Y")
        id_42 = Constant("42")

        # user(42, X) - can evaluate (ID is constant)
        self.assertTrue(pattern.can_evaluate_with(Atom(user, id_42, x)))

        # user(X, Y) - cannot evaluate (ID is variable)
        self.assertFalse(pattern.can_evaluate_with(Atom(user, x, y)))

        # user(X, Y) with {X -> 42} - can evaluate (ID resolves to constant)
        sub = Substitution({x: id_42})
        self.assertTrue(pattern.can_evaluate_with(Atom(user, x, y), sub))


if __name__ == "__main__":
    unittest.main()
