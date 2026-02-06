import unittest

from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.io.parsers.dlgpe.dlgpe_transformer import (
    DlgpeUnsupportedFeatureError,
)


class TestDlgpePrefixBaseStrict(unittest.TestCase):
    def test_relative_prefix_before_base_strict(self) -> None:
        text = """
            @prefix ex: <relative/ns/>.
            @base <http://example.org/base/>.
            ex:pred(a).
        """
        parser = DlgpeParser.create(strict_prefix_base=True)
        with self.assertRaises(DlgpeUnsupportedFeatureError):
            parser.parse(text)

    def test_relative_prefix_before_base_lenient(self) -> None:
        text = """
            @prefix ex: <relative/ns/>.
            @base <http://example.org/base/>.
            ex:pred(a).
        """
        parser = DlgpeParser.create(strict_prefix_base=False)
        result = parser.parse(text)
        header = result.get("header", {})
        self.assertEqual(
            "http://example.org/base/relative/ns/", header.get("prefixes", {}).get("ex")
        )


if __name__ == "__main__":
    unittest.main()
