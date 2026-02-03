import unittest

from prototyping_inference_engine.api.data.comparison_data import ComparisonDataSource
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.atom.predicate import comparison_predicate
from prototyping_inference_engine.api.atom.term.factory.literal_factory import LiteralFactory
from prototyping_inference_engine.api.atom.term.literal_config import (
    LiteralConfig,
    LiteralComparison,
    LiteralNormalization,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage


class TestComparisonDataSource(unittest.TestCase):
    def test_normalized_comparison(self):
        factory = LiteralFactory(DictStorage(), LiteralConfig.default())
        left = factory.create("01", "xsd:integer")
        right = factory.create("1", "xsd:integer")
        data = ComparisonDataSource(LiteralComparison.BY_NORMALIZED_VALUE)
        query = BasicQuery(comparison_predicate("!="), {0: left, 1: right}, {})
        self.assertEqual(list(data.evaluate(query)), [])

    def test_lexical_comparison(self):
        config = LiteralConfig(
            normalization=LiteralNormalization.NORMALIZED,
            comparison=LiteralComparison.BY_LEXICAL,
        )
        factory = LiteralFactory(DictStorage(), config)
        left = factory.create("01", "xsd:integer")
        right = factory.create("1", "xsd:integer")
        data = ComparisonDataSource(LiteralComparison.BY_LEXICAL)
        query = BasicQuery(comparison_predicate("!="), {0: left, 1: right}, {})
        self.assertEqual(list(data.evaluate(query)), [tuple()])


if __name__ == "__main__":
    unittest.main()
