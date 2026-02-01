"""
Unit tests for term factories.
"""
import gc
import unittest
from unittest import TestCase

from prototyping_inference_engine.api.atom.term.factory import (
    VariableFactory,
    ConstantFactory,
    PredicateFactory,
)
from prototyping_inference_engine.api.atom.term.storage import (
    DictStorage,
    WeakRefStorage,
)
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.predicate import Predicate


class TestVariableFactory(TestCase):
    """Tests for VariableFactory."""

    def test_create_returns_variable(self):
        """Test that create returns a Variable instance."""
        factory = VariableFactory(DictStorage())
        var = factory.create("X")
        self.assertIsInstance(var, Variable)
        self.assertEqual(str(var), "X")

    def test_create_same_identifier_returns_same_instance(self):
        """Test that creating with same identifier returns same instance."""
        factory = VariableFactory(DictStorage())
        var1 = factory.create("X")
        var2 = factory.create("X")
        self.assertIs(var1, var2)

    def test_create_different_identifiers_returns_different_instances(self):
        """Test that different identifiers create different instances."""
        factory = VariableFactory(DictStorage())
        var_x = factory.create("X")
        var_y = factory.create("Y")
        self.assertIsNot(var_x, var_y)

    def test_fresh_creates_unique_variable(self):
        """Test that fresh creates a unique variable."""
        factory = VariableFactory(DictStorage())
        fresh1 = factory.fresh()
        fresh2 = factory.fresh()
        self.assertIsNot(fresh1, fresh2)
        self.assertNotEqual(str(fresh1), str(fresh2))

    def test_fresh_avoids_existing_identifiers(self):
        """Test that fresh avoids existing identifiers."""
        factory = VariableFactory(DictStorage())
        # Pre-create _FV0
        factory.create("_FV0")
        fresh = factory.fresh()
        # Should skip _FV0 and use _FV1
        self.assertEqual(str(fresh), "_FV1")

    def test_tracked_returns_created_variables(self):
        """Test that tracked returns all created variables."""
        factory = VariableFactory(DictStorage())
        var_x = factory.create("X")
        var_y = factory.create("Y")
        tracked = factory.tracked
        self.assertEqual(tracked, {var_x, var_y})

    def test_len_returns_count(self):
        """Test that len returns the number of tracked variables."""
        factory = VariableFactory(DictStorage())
        self.assertEqual(len(factory), 0)
        factory.create("X")
        self.assertEqual(len(factory), 1)
        factory.create("Y")
        self.assertEqual(len(factory), 2)
        factory.create("X")  # Duplicate, shouldn't increase count
        self.assertEqual(len(factory), 2)


class TestVariableFactoryWithWeakRef(TestCase):
    """Tests for VariableFactory with WeakRefStorage.

    Note: Variable uses a global cache (Variable.variables), so instances
    are never truly garbage collected even if the WeakRefStorage loses
    its reference. The WeakRefStorage still works for tracking purposes,
    but the GC behavior is limited by the global cache.
    """

    def test_variable_retained_in_weak_ref_storage(self):
        """Test that variables are tracked in WeakRefStorage."""
        factory = VariableFactory(WeakRefStorage())
        var = factory.create("X")
        gc.collect()
        # Variable is retained because Variable class has global cache
        self.assertEqual(len(factory), 1)
        self.assertIn(var, factory.tracked)

    def test_weak_ref_storage_allows_clearing(self):
        """Test that WeakRefStorage can be cleared explicitly."""
        factory = VariableFactory(WeakRefStorage())
        factory.create("X")
        factory.create("Y")
        self.assertEqual(len(factory), 2)
        factory._storage.clear()
        self.assertEqual(len(factory), 0)


class TestConstantFactory(TestCase):
    """Tests for ConstantFactory."""

    def test_create_returns_constant(self):
        """Test that create returns a Constant instance."""
        factory = ConstantFactory(DictStorage())
        const = factory.create("a")
        self.assertIsInstance(const, Constant)
        self.assertEqual(str(const), "a")

    def test_create_same_identifier_returns_same_instance(self):
        """Test that creating with same identifier returns same instance."""
        factory = ConstantFactory(DictStorage())
        const1 = factory.create("a")
        const2 = factory.create("a")
        self.assertIs(const1, const2)

    def test_create_different_identifiers_returns_different_instances(self):
        """Test that different identifiers create different instances."""
        factory = ConstantFactory(DictStorage())
        const_a = factory.create("a")
        const_b = factory.create("b")
        self.assertIsNot(const_a, const_b)

    def test_create_with_non_string_identifier(self):
        """Test that constants can have non-string identifiers."""
        factory = ConstantFactory(DictStorage())
        const_int = factory.create(42)
        const_tuple = factory.create((1, 2, 3))
        self.assertEqual(const_int.identifier, 42)
        self.assertEqual(const_tuple.identifier, (1, 2, 3))

    def test_tracked_returns_created_constants(self):
        """Test that tracked returns all created constants."""
        factory = ConstantFactory(DictStorage())
        const_a = factory.create("a")
        const_b = factory.create("b")
        tracked = factory.tracked
        self.assertEqual(tracked, {const_a, const_b})

    def test_len_returns_count(self):
        """Test that len returns the number of tracked constants."""
        factory = ConstantFactory(DictStorage())
        self.assertEqual(len(factory), 0)
        factory.create("a")
        self.assertEqual(len(factory), 1)
        factory.create("b")
        self.assertEqual(len(factory), 2)


class TestConstantFactoryWithWeakRef(TestCase):
    """Tests for ConstantFactory with WeakRefStorage.

    Note: Constant uses @cache on __new__, so instances are never truly
    garbage collected even if the WeakRefStorage loses its reference.
    """

    def test_constant_retained_in_weak_ref_storage(self):
        """Test that constants are tracked in WeakRefStorage."""
        factory = ConstantFactory(WeakRefStorage())
        const = factory.create("a")
        gc.collect()
        # Constant is retained because Constant class has @cache
        self.assertEqual(len(factory), 1)
        self.assertIn(const, factory.tracked)

    def test_weak_ref_storage_allows_clearing(self):
        """Test that WeakRefStorage can be cleared explicitly."""
        factory = ConstantFactory(WeakRefStorage())
        factory.create("a")
        factory.create("b")
        self.assertEqual(len(factory), 2)
        factory._storage.clear()
        self.assertEqual(len(factory), 0)


class TestPredicateFactory(TestCase):
    """Tests for PredicateFactory."""

    def test_create_returns_predicate(self):
        """Test that create returns a Predicate instance."""
        factory = PredicateFactory(DictStorage())
        pred = factory.create("p", 2)
        self.assertIsInstance(pred, Predicate)
        self.assertEqual(pred.name, "p")
        self.assertEqual(pred.arity, 2)

    def test_create_same_name_arity_returns_same_instance(self):
        """Test that creating with same (name, arity) returns same instance."""
        factory = PredicateFactory(DictStorage())
        pred1 = factory.create("p", 2)
        pred2 = factory.create("p", 2)
        self.assertIs(pred1, pred2)

    def test_create_different_name_returns_different_instance(self):
        """Test that different names create different instances."""
        factory = PredicateFactory(DictStorage())
        pred_p = factory.create("p", 2)
        pred_q = factory.create("q", 2)
        self.assertIsNot(pred_p, pred_q)

    def test_create_different_arity_returns_different_instance(self):
        """Test that different arities create different instances."""
        factory = PredicateFactory(DictStorage())
        pred_p2 = factory.create("p", 2)
        pred_p3 = factory.create("p", 3)
        self.assertIsNot(pred_p2, pred_p3)

    def test_tracked_returns_created_predicates(self):
        """Test that tracked returns all created predicates."""
        factory = PredicateFactory(DictStorage())
        pred_p = factory.create("p", 2)
        pred_q = factory.create("q", 1)
        tracked = factory.tracked
        self.assertEqual(tracked, {pred_p, pred_q})

    def test_len_returns_count(self):
        """Test that len returns the number of tracked predicates."""
        factory = PredicateFactory(DictStorage())
        self.assertEqual(len(factory), 0)
        factory.create("p", 2)
        self.assertEqual(len(factory), 1)
        factory.create("q", 1)
        self.assertEqual(len(factory), 2)


class TestPredicateFactoryWithWeakRef(TestCase):
    """Tests for PredicateFactory with WeakRefStorage.

    Note: Predicate uses @cache on __new__, so instances are never truly
    garbage collected even if the WeakRefStorage loses its reference.
    """

    def test_predicate_retained_in_weak_ref_storage(self):
        """Test that predicates are tracked in WeakRefStorage."""
        factory = PredicateFactory(WeakRefStorage())
        pred = factory.create("p", 2)
        gc.collect()
        # Predicate is retained because Predicate class has @cache
        self.assertEqual(len(factory), 1)
        self.assertIn(pred, factory.tracked)

    def test_weak_ref_storage_allows_clearing(self):
        """Test that WeakRefStorage can be cleared explicitly."""
        factory = PredicateFactory(WeakRefStorage())
        factory.create("p", 2)
        factory.create("q", 1)
        self.assertEqual(len(factory), 2)
        factory._storage.clear()
        self.assertEqual(len(factory), 0)


class TestFactoryIntegration(TestCase):
    """Integration tests for factories working together."""

    def test_factories_share_storage_type_but_not_data(self):
        """Test that factories can use same storage type but have separate data."""
        var_storage = DictStorage()
        const_storage = DictStorage()
        pred_storage = DictStorage()

        var_factory = VariableFactory(var_storage)
        const_factory = ConstantFactory(const_storage)
        pred_factory = PredicateFactory(pred_storage)

        var = var_factory.create("X")
        const = const_factory.create("a")
        pred = pred_factory.create("p", 1)

        # Each factory has its own items
        self.assertEqual(len(var_factory), 1)
        self.assertEqual(len(const_factory), 1)
        self.assertEqual(len(pred_factory), 1)

        # Items are of correct type
        self.assertIn(var, var_factory.tracked)
        self.assertIn(const, const_factory.tracked)
        self.assertIn(pred, pred_factory.tracked)

    def test_factories_with_weak_ref_allow_independent_clearing(self):
        """Test that factories with WeakRefStorage allow independent clearing."""
        var_factory = VariableFactory(WeakRefStorage())
        const_factory = ConstantFactory(WeakRefStorage())

        var_factory.create("X")
        const = const_factory.create("a")

        # Clear only variable factory
        var_factory._storage.clear()

        # Variable factory should be empty, constant factory should remain
        self.assertEqual(len(var_factory), 0)
        self.assertEqual(len(const_factory), 1)
        self.assertIn(const, const_factory.tracked)


if __name__ == "__main__":
    unittest.main()
