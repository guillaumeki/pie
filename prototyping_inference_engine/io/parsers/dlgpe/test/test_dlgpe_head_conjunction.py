"""
Additional DLGPE head conjunction tests.
"""

import unittest

from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestDlgpeHeadConjunction(unittest.TestCase):
    """Test head conjunction parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_head_conjunction_single_disjunct(self):
        result = self.parser.parse("p(X), q(X) :- r(X).")
        self.assertEqual(len(result["rules"]), 1)
        rule = result["rules"][0]

        self.assertEqual(len(rule.head_disjuncts), 1)
        head_formula = rule.head_disjuncts[0]
        self.assertEqual(len(head_formula.atoms), 2)
        predicates = {atom.predicate.name for atom in head_formula.atoms}
        self.assertEqual(predicates, {"p", "q"})


if __name__ == "__main__":
    unittest.main()
