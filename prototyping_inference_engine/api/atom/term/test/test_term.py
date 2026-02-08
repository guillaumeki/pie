from unittest import TestCase

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestVariable(TestCase):
    def test_flyweight_pattern(self):
        """Test that Variable uses flyweight pattern - same identifier returns same instance."""
        v1 = Variable("X")
        v2 = Variable("X")
        self.assertIs(v1, v2)

    def test_different_identifiers_different_instances(self):
        """Test that different identifiers create different instances."""
        v1 = Variable("X")
        v2 = Variable("Y")
        self.assertIsNot(v1, v2)

    def test_identifier_property(self):
        """Test that identifier property returns the correct value."""
        v = Variable("X")
        self.assertEqual(v.identifier, "X")

    def test_str(self):
        """Test string representation."""
        v = Variable("X")
        self.assertEqual(v.identifier, "X")

    def test_repr(self):
        """Test repr representation."""
        v = Variable("X")
        self.assertEqual(v.identifier, "X")

    def test_is_term(self):
        """Test that Variable is a subclass of Term."""
        v = Variable("X")
        self.assertIsInstance(v, Term)

    def test_fresh_variable(self):
        """Test that fresh_variable creates a new unique variable."""
        v1 = Variable.fresh_variable()
        v2 = Variable.fresh_variable()
        self.assertIsNot(v1, v2)
        self.assertNotEqual(v1.identifier, v2.identifier)

    def test_safe_renaming(self):
        """Test that safe_renaming creates a new variable different from original."""
        v = Variable("X")
        renamed = Variable.safe_renaming(v)
        self.assertIsNot(v, renamed)
        self.assertNotEqual(v.identifier, renamed.identifier)

    def test_safe_renaming_substitution(self):
        """Test that safe_renaming_substitution creates substitution for all variables."""
        v1 = Variable("X")
        v2 = Variable("Y")
        sub = Variable.safe_renaming_substitution([v1, v2])
        self.assertIsInstance(sub, Substitution)
        self.assertIn(v1, sub)
        self.assertIn(v2, sub)
        # The renamed variables should be different from originals
        self.assertIsNot(sub[v1], v1)
        self.assertIsNot(sub[v2], v2)

    def test_apply_substitution_mapped(self):
        """Test applying substitution when variable is in substitution."""
        v = Variable("X")
        c = Constant("a")
        sub = Substitution({v: c})
        result = v.apply_substitution(sub)
        self.assertEqual(result, c)

    def test_apply_substitution_not_mapped(self):
        """Test applying substitution when variable is not in substitution."""
        v = Variable("X")
        other = Variable("Y")
        c = Constant("a")
        sub = Substitution({other: c})
        result = v.apply_substitution(sub)
        self.assertIs(result, v)


class TestConstant(TestCase):
    def test_caching(self):
        """Test that Constant uses caching - same identifier returns same instance."""
        c1 = Constant("a")
        c2 = Constant("a")
        self.assertIs(c1, c2)

    def test_different_identifiers_different_instances(self):
        """Test that different identifiers create different instances."""
        c1 = Constant("a")
        c2 = Constant("b")
        self.assertIsNot(c1, c2)

    def test_identifier_property(self):
        """Test that identifier property returns the correct value."""
        c = Constant("a")
        self.assertEqual(c.identifier, "a")

    def test_str(self):
        """Test string representation."""
        c = Constant("a")
        self.assertEqual(c.identifier, "a")

    def test_repr(self):
        """Test repr representation."""
        c = Constant("a")
        self.assertEqual(c.identifier, "a")

    def test_is_term(self):
        """Test that Constant is a subclass of Term."""
        c = Constant("a")
        self.assertIsInstance(c, Term)

    def test_apply_substitution_unchanged(self):
        """Test that applying substitution to constant returns the same constant."""
        c = Constant("a")
        v = Variable("X")
        sub = Substitution({v: Constant("b")})
        result = c.apply_substitution(sub)
        self.assertIs(result, c)

    def test_numeric_identifier(self):
        """Test constant with numeric identifier."""
        c = Constant(42)
        self.assertEqual(c.identifier, 42)
        self.assertIsInstance(c.identifier, int)
