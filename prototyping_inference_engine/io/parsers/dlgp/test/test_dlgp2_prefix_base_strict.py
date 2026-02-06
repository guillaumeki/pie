import unittest

from prototyping_inference_engine.io.parsers.dlgp.dlgp2_parser import Dlgp2Parser
from prototyping_inference_engine.io.parsers.dlgp.dlgp2_transformer import (
    Dlgp2Transformer,
)


class TestDlgp2PrefixBaseStrict(unittest.TestCase):
    def test_relative_prefix_before_base_strict(self) -> None:
        text = "@prefix ex: <relative/ns/> @base <http://example.org/base/> ex:pred(a)."
        parser = Dlgp2Parser.instance()
        with self.assertRaises(ValueError):
            parser.parse(text)

    def test_relative_prefix_before_base_lenient(self) -> None:
        text = "@prefix ex: <relative/ns/> @base <http://example.org/base/> ex:pred(a)."
        transformer = Dlgp2Transformer(strict_prefix_base=False)
        parser = Dlgp2Parser.create(transformer)
        parsed = parser.parse(text)
        header = parsed.get("header", {})
        self.assertEqual(
            "http://example.org/base/relative/ns/", header.get("prefixes", {}).get("ex")
        )


if __name__ == "__main__":
    unittest.main()
