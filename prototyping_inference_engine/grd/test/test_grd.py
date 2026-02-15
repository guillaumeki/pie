import unittest

from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestGRD(unittest.TestCase):
    def test_positive_dependency(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(X) :- p(X).
                s(X) :- q(X).
                """
            )
        )
        grd = GRD(rules)
        r1, r2 = rules
        self.assertIn(r2, grd.get_triggered_rules(r1))

    def test_disjunctive_head_dependency(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(X) | r(X) :- p(X).
                s(X) :- r(X).
                """
            )
        )
        grd = GRD(rules)
        r1, r2 = rules
        self.assertIn(r2, grd.get_triggered_rules(r1))
