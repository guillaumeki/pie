"""Tests for collection protocols."""

import unittest

from prototyping_inference_engine.api.data.collection.protocols import (
    Queryable,
    Materializable,
    DynamicPredicates,
)
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.io.parsers.dlgp.dlgp2_parser import Dlgp2Parser


class TestQueryableProtocol(unittest.TestCase):
    """Test Queryable protocol."""

    def test_frozen_fact_base_is_queryable(self):
        """Test that FrozenInMemoryFactBase implements Queryable."""
        fb = FrozenInMemoryFactBase()
        self.assertIsInstance(fb, Queryable)

    def test_mutable_fact_base_is_queryable(self):
        """Test that MutableInMemoryFactBase implements Queryable."""
        fb = MutableInMemoryFactBase()
        self.assertIsInstance(fb, Queryable)

    def test_readable_data_subclass_is_queryable(self):
        """Test that ReadableData subclasses are Queryable."""
        parser = Dlgp2Parser.instance()
        fb = FrozenInMemoryFactBase(parser.parse_atoms("p(a)."))
        # ReadableData should satisfy Queryable protocol
        self.assertIsInstance(fb, Queryable)

    def test_non_queryable_class(self):
        """Test that arbitrary classes are not Queryable."""

        class NotQueryable:
            pass

        self.assertNotIsInstance(NotQueryable(), Queryable)

    def test_partial_implementation_not_queryable(self):
        """Test that partial implementations are not Queryable."""

        class PartialQueryable:
            def get_predicates(self):
                return iter([])

            # Missing: has_predicate, get_atomic_pattern, evaluate, can_evaluate

        self.assertNotIsInstance(PartialQueryable(), Queryable)


class TestMaterializableProtocol(unittest.TestCase):
    """Test Materializable protocol."""

    def test_frozen_fact_base_is_materializable(self):
        """Test that FrozenInMemoryFactBase implements Materializable."""
        fb = FrozenInMemoryFactBase()
        self.assertIsInstance(fb, Materializable)

    def test_mutable_fact_base_is_materializable(self):
        """Test that MutableInMemoryFactBase implements Materializable."""
        fb = MutableInMemoryFactBase()
        self.assertIsInstance(fb, Materializable)

    def test_non_materializable_class(self):
        """Test that arbitrary classes are not Materializable."""

        class NotMaterializable:
            pass

        self.assertNotIsInstance(NotMaterializable(), Materializable)

    def test_partial_implementation_not_materializable(self):
        """Test that partial implementations are not Materializable."""

        class PartialMaterializable:
            def __iter__(self):
                return iter([])

            def __len__(self):
                return 0

            # Missing: __contains__, variables, constants, terms

        self.assertNotIsInstance(PartialMaterializable(), Materializable)


class TestDynamicPredicatesProtocol(unittest.TestCase):
    """Test DynamicPredicates protocol."""

    def test_fact_base_is_dynamic_predicates(self):
        """Test that fact bases implement DynamicPredicates (have get_predicates)."""
        fb = FrozenInMemoryFactBase()
        self.assertIsInstance(fb, DynamicPredicates)

    def test_custom_dynamic_source(self):
        """Test custom class implementing DynamicPredicates."""

        class DynamicSource:
            def __init__(self):
                self._predicates = []

            def get_predicates(self):
                return iter(self._predicates)

            def add_predicate(self, pred):
                self._predicates.append(pred)

        source = DynamicSource()
        self.assertIsInstance(source, DynamicPredicates)

    def test_non_dynamic_class(self):
        """Test that classes without get_predicates are not DynamicPredicates."""

        class NotDynamic:
            pass

        self.assertNotIsInstance(NotDynamic(), DynamicPredicates)


class TestProtocolCombinations(unittest.TestCase):
    """Test protocol combinations."""

    def test_fact_base_is_both_queryable_and_materializable(self):
        """Test that fact bases implement both protocols."""
        fb = FrozenInMemoryFactBase()
        self.assertIsInstance(fb, Queryable)
        self.assertIsInstance(fb, Materializable)
        self.assertIsInstance(fb, DynamicPredicates)

    def test_queryable_only_source(self):
        """Test a source that is Queryable but not Materializable."""

        class QueryableOnly:
            def get_predicates(self):
                return iter([])

            def has_predicate(self, predicate):
                return False

            def get_atomic_pattern(self, predicate):
                raise KeyError()

            def evaluate(self, query):
                return iter([])

            def can_evaluate(self, query):
                return False

        source = QueryableOnly()
        self.assertIsInstance(source, Queryable)
        self.assertNotIsInstance(source, Materializable)


if __name__ == "__main__":
    unittest.main()
