"""
DLGPE compatibility tests inspired by Integraal DLGP tests.
"""

import unittest

from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.parser.dlgpe import DlgpeParser


class TestDlgpeCompatibility(unittest.TestCase):
    """DLGPE is expected to accept DLGP-style inputs where applicable."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_parse_single_fact(self):
        result = self.parser.parse("p1(a).")
        self.assertEqual(len(result["facts"]), 1)

    def test_parse_fact_with_variable(self):
        result = self.parser.parse("p1(X).")
        self.assertEqual(len(result["facts"]), 1)

    def test_parse_multiple_facts(self):
        result = self.parser.parse("p1(a), q1(b).")
        self.assertEqual(len(result["facts"]), 2)

    def test_parse_rules_section(self):
        result = self.parser.parse("@rules q1(X) :- p1(a).")
        self.assertEqual(len(result["rules"]), 1)

    def test_parse_facts_and_rules_sections(self):
        result = self.parser.parse("@facts p1(a). @rules q1(X) :- p1(a).")
        self.assertEqual(len(result["facts"]), 1)
        self.assertEqual(len(result["rules"]), 1)

    def test_parse_query(self):
        result = self.parser.parse("?(X) :- p1(X).")
        self.assertEqual(len(result["queries"]), 1)
        self.assertIsInstance(result["queries"][0], FOQuery)

    def test_parse_queries_section(self):
        result = self.parser.parse("@queries ?(X) :- p1(X).")
        self.assertEqual(len(result["queries"]), 1)

    def test_parse_query_with_equality(self):
        result = self.parser.parse("?(X) :- p1(a), X = b.")
        self.assertEqual(len(result["queries"]), 1)

    def test_parse_rule_with_ground_neck(self):
        result = self.parser.parse("q(X) ::- p(X).")
        self.assertEqual(len(result["rules"]), 1)

    def test_parse_constraints_section(self):
        result = self.parser.parse("@constraints ! :- p(X), q(X).")
        self.assertEqual(len(result["constraints"]), 1)

    def test_parse_rule_with_disjunctive_head(self):
        result = self.parser.parse("p(X) | q(X) :- r(X).")
        self.assertEqual(len(result["rules"]), 1)
        self.assertEqual(len(result["rules"][0].head), 2)

    def test_parse_rule_with_head_conjunction(self):
        result = self.parser.parse("p(X), q(X) :- r(X).")
        self.assertEqual(len(result["rules"]), 1)
        self.assertEqual(len(result["rules"][0].head), 1)
        self.assertEqual(len(result["rules"][0].head[0].atoms), 2)

    def test_parse_query_with_negation(self):
        result = self.parser.parse("?(X) :- p(X), not q(X).")
        self.assertEqual(len(result["queries"]), 1)


if __name__ == "__main__":
    unittest.main()
