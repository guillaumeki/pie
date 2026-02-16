import unittest

from prototyping_inference_engine.api.iri.normalization import (
    ExtendedComposableNormalizer,
    RFCNormalizationScheme,
    StandardComposableNormalizer,
    _normalize_pct_extended,
    _normalize_pct_standard,
)


class TestNormalizerExtras(unittest.TestCase):
    def test_expand_syntax_scheme(self) -> None:
        normalizer = StandardComposableNormalizer(RFCNormalizationScheme.SYNTAX)
        self.assertTrue(normalizer.has(RFCNormalizationScheme.CASE))
        self.assertTrue(normalizer.has(RFCNormalizationScheme.CHARACTER))
        self.assertTrue(normalizer.has(RFCNormalizationScheme.PCT))

    def test_normalize_port_removes_default(self) -> None:
        normalizer = StandardComposableNormalizer(RFCNormalizationScheme.SCHEME)
        self.assertIsNone(normalizer.normalize_port("80", "http"))
        self.assertEqual("8080", normalizer.normalize_port("8080", "http"))

    def test_normalize_path_authority_empty(self) -> None:
        normalizer = StandardComposableNormalizer()
        self.assertEqual("/", normalizer.normalize_path("", "http", True))

    def test_normalize_path_removes_dot_segments(self) -> None:
        normalizer = StandardComposableNormalizer(RFCNormalizationScheme.PATH)
        self.assertEqual("/a/c", normalizer.normalize_path("/a/b/../c", "http", True))

    def test_normalize_pct_standard(self) -> None:
        self.assertEqual("~", _normalize_pct_standard("%7E", uppercase=True))
        self.assertEqual("%2F", _normalize_pct_standard("%2f", uppercase=True))

    def test_normalize_pct_extended(self) -> None:
        self.assertEqual("\u00e9", _normalize_pct_extended("%C3%A9", uppercase=True))
        self.assertEqual("%C3%28", _normalize_pct_extended("%C3%28", uppercase=True))

    def test_extended_host_lowercases_and_uppercased_pct(self) -> None:
        normalizer = ExtendedComposableNormalizer(
            RFCNormalizationScheme.CASE, RFCNormalizationScheme.PCT
        )
        self.assertEqual(
            "example.com%3A80", normalizer.normalize_host("Example.COM%3a80")
        )


if __name__ == "__main__":
    unittest.main()
