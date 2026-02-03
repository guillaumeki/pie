"""
Additional DLGPE unsupported feature tests.
"""
import unittest

from prototyping_inference_engine.parser.dlgpe import (
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

    def test_unsupported_arithmetic(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("p(X + 1).")
        self.assertIn("Arithmetic expressions", str(ctx.exception))

    def test_unsupported_functional_term(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("p(f(X)).")
        self.assertIn("Functional terms", str(ctx.exception))

    def test_unsupported_subquery(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("h(X) :- Q := p(X).")
        self.assertIn("Subqueries", str(ctx.exception))

    def test_unsupported_repeated_atom(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("h(X) :- p*(X, Y).")
        self.assertIn("Repeated atoms", str(ctx.exception))

    def test_unsupported_pattern_predicate(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse("$p(a).")
        self.assertIn("Pattern predicates", str(ctx.exception))

    def test_unsupported_json_metadata(self):
        with self.assertRaises(DlgpeUnsupportedFeatureError) as ctx:
            self.parser.parse('{"name": "rule1"} p(a).')
        self.assertIn("JSON metadata", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
