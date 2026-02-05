import unittest

from prototyping_inference_engine.iri.iri import IRIRef
from prototyping_inference_engine.iri.normalization import (
    ExtendedComposableNormalizer,
    RFCNormalizationScheme,
    StandardComposableNormalizer,
)


class TestStandardComposableNormalizer(unittest.TestCase):
    def test_pct_decodes_unreserved_in_userinfo(self) -> None:
        data = [
            ("%7E%41", "~A"),
            ("%7e%3a%20%25", "~%3a%20%25"),
            ("user%7e%3a%41", "user~%3aA"),
            ("Already%20encoded", "Already%20encoded"),
        ]
        normalizer = StandardComposableNormalizer(RFCNormalizationScheme.PCT)
        for input_value, expected in data:
            with self.subTest(value=input_value):
                self.assertEqual(
                    expected, normalizer.normalize_user_info(input_value, "http")
                )

    def test_character_mode_normalizes_unicode(self) -> None:
        decomposed = "u\u0301ser"
        composed = "\u00faser"

        normalizer_no_char = StandardComposableNormalizer()
        no_char1 = normalizer_no_char.normalize_user_info(decomposed, "http")
        no_char2 = normalizer_no_char.normalize_user_info(composed, "http")
        self.assertNotEqual(no_char1, no_char2)

        normalizer_char = StandardComposableNormalizer(RFCNormalizationScheme.CHARACTER)
        char1 = normalizer_char.normalize_user_info(decomposed, "http")
        char2 = normalizer_char.normalize_user_info(composed, "http")
        self.assertEqual(char1, char2)

    def test_host_ascii_lowercased_and_pct_uppercased(self) -> None:
        normalizer = StandardComposableNormalizer(
            RFCNormalizationScheme.SYNTAX, RFCNormalizationScheme.SCHEME
        )
        iri = IRIRef("HttP://ExAmPle.COM%3a80/")
        norm = iri.normalize_in_place(normalizer)
        self.assertEqual("http://example.com%3A80/", norm.recompose())


class TestExtendedComposableNormalizer(unittest.TestCase):
    def test_pct_decodes_unreserved_in_userinfo(self) -> None:
        data = [
            ("%7E%41", "~A"),
            ("%7e%3a%20%25", "~%3a%20%25"),
            ("user%7e%3a%41", "user~%3aA"),
            ("Already%20encoded", "Already%20encoded"),
        ]
        normalizer = ExtendedComposableNormalizer(RFCNormalizationScheme.PCT)
        for input_value, expected in data:
            with self.subTest(value=input_value):
                self.assertEqual(
                    expected, normalizer.normalize_user_info(input_value, "http")
                )

    def test_pct_decodes_iunreserved_in_userinfo(self) -> None:
        data = [
            ("%7E%41", "~A"),
            ("%C3%A9", "\u00e9"),
            ("%E2%82%AC", "\u20ac"),
            ("%F0%9F%98%80", "\U0001f600"),
            ("%7E%C3%A9%E2%82%AC", "~\u00e9\u20ac"),
            ("%20%25", "%20%25"),
            ("%C3%28", "%C3%28"),
            ("%C3%28%C3%A9", "%C3%28\u00e9"),
        ]
        normalizer = ExtendedComposableNormalizer(RFCNormalizationScheme.PCT)
        for input_value, expected in data:
            with self.subTest(value=input_value):
                self.assertEqual(
                    expected, normalizer.normalize_user_info(input_value, "http")
                )

    def test_character_mode_normalizes_unicode(self) -> None:
        decomposed = "u\u0301ser"
        composed = "\u00faser"

        normalizer_no_char = ExtendedComposableNormalizer()
        no_char1 = normalizer_no_char.normalize_user_info(decomposed, "http")
        no_char2 = normalizer_no_char.normalize_user_info(composed, "http")
        self.assertNotEqual(no_char1, no_char2)

        normalizer_char = ExtendedComposableNormalizer(RFCNormalizationScheme.CHARACTER)
        char1 = normalizer_char.normalize_user_info(decomposed, "http")
        char2 = normalizer_char.normalize_user_info(composed, "http")
        self.assertEqual(char1, char2)

    def test_ipct_then_character(self) -> None:
        decomposed = "u\u0301ser"
        composed_pct = "%C3%BAser"

        ipct_only = ExtendedComposableNormalizer(RFCNormalizationScheme.PCT)
        no_char1 = ipct_only.normalize_user_info(decomposed, "http")
        no_char2 = ipct_only.normalize_user_info(composed_pct, "http")
        self.assertNotEqual(no_char1, no_char2)

        ipct_char = ExtendedComposableNormalizer(
            RFCNormalizationScheme.PCT, RFCNormalizationScheme.CHARACTER
        )
        char1 = ipct_char.normalize_user_info(decomposed, "http")
        char2 = ipct_char.normalize_user_info(composed_pct, "http")
        self.assertEqual(char1, char2)

    def test_host_ascii_lowercased_and_pct_uppercased(self) -> None:
        normalizer = ExtendedComposableNormalizer(
            RFCNormalizationScheme.SYNTAX, RFCNormalizationScheme.SCHEME
        )
        iri = IRIRef("HttP://ExAmPle.COM%3a80/")
        norm = iri.normalize_in_place(normalizer)
        self.assertEqual("http://example.com%3A80/", norm.recompose())


if __name__ == "__main__":
    unittest.main()
