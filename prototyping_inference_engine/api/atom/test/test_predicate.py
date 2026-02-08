from unittest import TestCase

from prototyping_inference_engine.api.atom.predicate import Predicate, SpecialPredicate


class TestPredicate(TestCase):
    def test_caching(self):
        """Test that Predicate uses caching - same name and arity returns same instance."""
        p1 = Predicate("p", 2)
        p2 = Predicate("p", 2)
        self.assertIs(p1, p2)

    def test_different_name_different_instances(self):
        """Test that different names create different instances."""
        p1 = Predicate("p", 2)
        p2 = Predicate("q", 2)
        self.assertIsNot(p1, p2)

    def test_different_arity_different_instances(self):
        """Test that different arities create different instances."""
        p1 = Predicate("p", 1)
        p2 = Predicate("p", 2)
        self.assertIsNot(p1, p2)

    def test_name_property(self):
        """Test that name property returns the correct value."""
        p = Predicate("myPredicate", 3)
        self.assertEqual(p.name, "myPredicate")

    def test_arity_property(self):
        """Test that arity property returns the correct value."""
        p = Predicate("p", 3)
        self.assertEqual(p.arity, 3)

    def test_str(self):
        """Test string representation returns just the name."""
        p = Predicate("p", 2)
        self.assertEqual(p.name, "p")

    def test_repr(self):
        """Test repr representation includes arity."""
        p = Predicate("p", 2)
        self.assertEqual(p.arity, 2)

    def test_zero_arity(self):
        """Test predicate with zero arity (propositional)."""
        p = Predicate("prop", 0)
        self.assertEqual(p.arity, 0)
        self.assertEqual(p.name, "prop")


class TestSpecialPredicate(TestCase):
    def test_equality_predicate(self):
        """Test that EQUALITY special predicate exists and has correct properties."""
        eq = SpecialPredicate.EQUALITY.value
        self.assertIsInstance(eq, Predicate)
        self.assertEqual(eq.name, "=")
        self.assertEqual(eq.arity, 2)

    def test_equality_predicate_is_cached(self):
        """Test that the equality predicate is the same as Predicate('=', 2)."""
        eq = SpecialPredicate.EQUALITY.value
        p = Predicate("=", 2)
        self.assertIs(eq, p)
