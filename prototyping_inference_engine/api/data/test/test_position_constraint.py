"""Tests for position constraints."""
import unittest

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.constraint import (
    PositionConstraint,
    GroundConstraint,
    ConstantConstraint,
    VariableConstraint,
    PredicateConstraint,
    AnyOfConstraint,
    AllOfConstraint,
    GROUND,
    CONSTANT,
    VARIABLE,
)


class TestGroundConstraint(unittest.TestCase):
    """Test GroundConstraint."""

    def test_constant_satisfies(self):
        """Constants satisfy ground constraint."""
        self.assertTrue(GROUND.is_satisfied_by(Constant("a")))

    def test_variable_does_not_satisfy(self):
        """Variables do not satisfy ground constraint."""
        self.assertFalse(GROUND.is_satisfied_by(Variable("X")))

    def test_description(self):
        """Test description."""
        self.assertEqual(GROUND.description, "ground")


class TestConstantConstraint(unittest.TestCase):
    """Test ConstantConstraint."""

    def test_constant_satisfies(self):
        """Constants satisfy constant constraint."""
        self.assertTrue(CONSTANT.is_satisfied_by(Constant("a")))

    def test_variable_does_not_satisfy(self):
        """Variables do not satisfy constant constraint."""
        self.assertFalse(CONSTANT.is_satisfied_by(Variable("X")))

    def test_description(self):
        """Test description."""
        self.assertEqual(CONSTANT.description, "constant")


class TestVariableConstraint(unittest.TestCase):
    """Test VariableConstraint."""

    def test_variable_satisfies(self):
        """Variables satisfy variable constraint."""
        self.assertTrue(VARIABLE.is_satisfied_by(Variable("X")))

    def test_constant_does_not_satisfy(self):
        """Constants do not satisfy variable constraint."""
        self.assertFalse(VARIABLE.is_satisfied_by(Constant("a")))

    def test_description(self):
        """Test description."""
        self.assertEqual(VARIABLE.description, "variable")


class TestPredicateConstraint(unittest.TestCase):
    """Test PredicateConstraint."""

    def test_custom_predicate(self):
        """Test custom predicate constraint."""
        # Constraint: constant must start with 'a'
        constraint = PredicateConstraint(
            lambda t: isinstance(t, Constant) and t.identifier.startswith("a"),
            "starts with 'a'"
        )
        self.assertTrue(constraint.is_satisfied_by(Constant("abc")))
        self.assertFalse(constraint.is_satisfied_by(Constant("xyz")))
        self.assertFalse(constraint.is_satisfied_by(Variable("X")))

    def test_description(self):
        """Test description."""
        constraint = PredicateConstraint(lambda t: True, "always true")
        self.assertEqual(constraint.description, "always true")


class TestAnyOfConstraint(unittest.TestCase):
    """Test AnyOfConstraint (OR)."""

    def test_any_satisfied(self):
        """At least one constraint satisfied."""
        constraint = AnyOfConstraint(CONSTANT, VARIABLE)
        self.assertTrue(constraint.is_satisfied_by(Constant("a")))
        self.assertTrue(constraint.is_satisfied_by(Variable("X")))

    def test_none_satisfied(self):
        """No constraint satisfied - should fail."""
        # This constraint can never be satisfied (constant AND variable)
        constraint = AnyOfConstraint(
            AllOfConstraint(CONSTANT, VARIABLE)  # Impossible
        )
        self.assertFalse(constraint.is_satisfied_by(Constant("a")))
        self.assertFalse(constraint.is_satisfied_by(Variable("X")))

    def test_description(self):
        """Test description."""
        constraint = AnyOfConstraint(CONSTANT, VARIABLE)
        self.assertEqual(constraint.description, "(constant | variable)")

    def test_empty_raises(self):
        """Empty AnyOfConstraint should raise."""
        with self.assertRaises(ValueError):
            AnyOfConstraint()

    def test_or_operator(self):
        """Test | operator creates AnyOfConstraint."""
        constraint = CONSTANT | VARIABLE
        self.assertIsInstance(constraint, AnyOfConstraint)
        self.assertTrue(constraint.is_satisfied_by(Constant("a")))
        self.assertTrue(constraint.is_satisfied_by(Variable("X")))


class TestAllOfConstraint(unittest.TestCase):
    """Test AllOfConstraint (AND)."""

    def test_all_satisfied(self):
        """All constraints satisfied."""
        constraint = AllOfConstraint(GROUND, CONSTANT)
        self.assertTrue(constraint.is_satisfied_by(Constant("a")))

    def test_one_not_satisfied(self):
        """One constraint not satisfied - should fail."""
        constraint = AllOfConstraint(GROUND, CONSTANT)
        self.assertFalse(constraint.is_satisfied_by(Variable("X")))

    def test_description(self):
        """Test description."""
        constraint = AllOfConstraint(GROUND, CONSTANT)
        self.assertEqual(constraint.description, "(ground & constant)")

    def test_empty_raises(self):
        """Empty AllOfConstraint should raise."""
        with self.assertRaises(ValueError):
            AllOfConstraint()

    def test_and_operator(self):
        """Test & operator creates AllOfConstraint."""
        constraint = GROUND & CONSTANT
        self.assertIsInstance(constraint, AllOfConstraint)
        self.assertTrue(constraint.is_satisfied_by(Constant("a")))
        self.assertFalse(constraint.is_satisfied_by(Variable("X")))


class TestCompositeConstraints(unittest.TestCase):
    """Test complex constraint compositions."""

    def test_nested_composition(self):
        """Test nested AND/OR composition."""
        # (constant | variable) & ground
        constraint = (CONSTANT | VARIABLE) & GROUND
        self.assertTrue(constraint.is_satisfied_by(Constant("a")))
        self.assertFalse(constraint.is_satisfied_by(Variable("X")))


if __name__ == "__main__":
    unittest.main()
