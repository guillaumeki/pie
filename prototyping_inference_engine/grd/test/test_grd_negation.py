import unittest

from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestGRDNegation(unittest.TestCase):
    def test_negative_dependency(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(X) :- p(X).
                s(X) :- t(X), not q(X).
                """
            )
        )
        grd = GRD(rules)
        r1, r2 = rules
        self.assertIn(r2, grd.get_prevented_rules(r1))

    def test_unsafe_negation_raises(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(X) :- p(X).
                s(X) :- not q(Y).
                """
            )
        )
        with self.assertRaises(ValueError):
            GRD(rules)
