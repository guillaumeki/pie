import unittest

from prototyping_inference_engine.api.atom.term.factory.literal_factory import LiteralFactory
from prototyping_inference_engine.api.atom.term.literal_config import (
    LiteralConfig,
    LiteralNormalization,
    LiteralComparison,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage


class TestLiteralFactoryDefaults(unittest.TestCase):
    def test_normalized_integer(self):
        factory = LiteralFactory(DictStorage(), LiteralConfig.default())
        lit = factory.create("01", "xsd:integer")
        self.assertEqual(lit.value, 1)
        self.assertEqual(str(lit), "1")
        self.assertEqual(lit.datatype, "xsd:integer")

    def test_language_literal(self):
        factory = LiteralFactory(DictStorage(), LiteralConfig.default())
        lit = factory.create("chat", lang="fr")
        self.assertEqual(lit.lang, "fr")
        self.assertEqual(str(lit), "\"chat\"@fr")


class TestLiteralFactoryConfig(unittest.TestCase):
    def test_raw_lexical_comparison(self):
        config = LiteralConfig(
            normalization=LiteralNormalization.RAW_LEXICAL,
            comparison=LiteralComparison.BY_LEXICAL,
            keep_lexical=False,
        )
        factory = LiteralFactory(DictStorage(), config)
        lit = factory.create("01", "xsd:integer")
        self.assertEqual(lit.value, "01")
        self.assertIsNone(lit.lexical)
        self.assertEqual(lit.comparison_key, ("xsd:integer", "01", None))
        self.assertEqual(str(lit), "01")
