"""
Additional DLGPE head conjunction tests.
"""
import unittest

from prototyping_inference_engine.parser.dlgpe import DlgpeParser


class TestDlgpeHeadConjunction(unittest.TestCase):
    """Test head conjunction parsing."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_head_conjunction_single_disjunct(self):
        result = self.parser.parse("p(X), q(X) :- r(X).")
        self.assertEqual(len(result["rules"]), 1)
        rule = result["rules"][0]

        self.assertEqual(len(rule.head), 1)
        head_cq = rule.head[0]
        self.assertEqual(len(head_cq.atoms), 2)
        predicates = {atom.predicate.name for atom in head_cq.atoms}
        self.assertEqual(predicates, {"p", "q"})


if __name__ == "__main__":
    unittest.main()
