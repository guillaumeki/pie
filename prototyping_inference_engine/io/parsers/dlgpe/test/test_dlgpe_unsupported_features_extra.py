"""
Additional DLGPE unsupported feature tests.
"""

import unittest

from prototyping_inference_engine.io.parsers.dlgpe import (
    DlgpeParser,
    DlgpeUnsupportedFeatureError,
)


class TestDlgpeUnsupportedFeaturesExtra(unittest.TestCase):
    """Extra unsupported feature cases inspired by external parsers."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_unsupported_operator(self):
        result = self.parser.parse("?(X) :- X < Y.")
        self.assertEqual(len(result["queries"]), 1)

    def test_computed_directive_accepts_non_stdfct(self):
        result = self.parser.parse("@computed ex: <http://example.org/functions#>.")
        header = result.get("header", {})
        self.assertIsInstance(header, dict)
        self.assertIn("computed", header)
        self.assertEqual(header["computed"].get("ex"), "http://example.org/functions#")

    def test_unsupported_functional_term(self):
        result = self.parser.parse("p(f(X)).")
        self.assertEqual(len(result["facts"]), 1)

    def test_unsupported_subquery(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("h(X) :- Q := p(X).")
        self.assertIn("Subqueries", ctx.exception.args[0])

    def test_unsupported_repeated_atom(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("h(X) :- p*(X, Y).")
        self.assertIn("Repeated atoms", ctx.exception.args[0])

    def test_unsupported_pattern_predicate(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("$p(a).")
        self.assertIn("Pattern predicates", ctx.exception.args[0])

    def test_unsupported_json_metadata(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse('{"name": "rule1"} p(a).')
        self.assertIn("JSON metadata", ctx.exception.args[0])


if __name__ == "__main__":
    unittest.main()
