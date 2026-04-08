import unittest

from prototyping_inference_engine.rule_analysis.fragments import extract_rule_fragments
from prototyping_inference_engine.rule_analysis.test._helpers import only_rule


class TestRuleFragments(unittest.TestCase):
    def test_extracts_positive_and_negative_body_atoms(self):
        rule = only_rule("q(X) :- p(X), not r(X).")

        fragments = extract_rule_fragments(rule)

        self.assertEqual(
            {atom.predicate.name for atom in fragments.positive_body}, {"p"}
        )
        self.assertEqual(
            {atom.predicate.name for atom in fragments.negative_body}, {"r"}
        )
        self.assertFalse(fragments.is_positive)

    def test_extracts_disjunctive_head_atoms(self):
        rule = only_rule("q(X) | r(X) :- p(X).")

        fragments = extract_rule_fragments(rule)

        self.assertTrue(fragments.has_disjunctive_head)
        self.assertEqual(len(fragments.head_disjuncts), 2)
        self.assertEqual(
            {atom.predicate.name for atom in fragments.all_head_atoms},
            {"q", "r"},
        )


if __name__ == "__main__":
    unittest.main()
