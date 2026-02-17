import unittest

from prototyping_inference_engine.grd.grd import (
    GRD,
    DependencyComputationMode,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestGrdPredicateMode(unittest.TestCase):
    def test_predicate_mode_adds_coarse_edges(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(a) :- p(X).
                s(X) :- q(b).
                """
            )
        )
        r1, r2 = rules

        unifier_grd = GRD(rules, mode=DependencyComputationMode.UNIFIER)
        predicate_grd = GRD(rules, mode=DependencyComputationMode.PREDICATE)

        self.assertNotIn(r2, unifier_grd.get_triggered_rules(r1))
        self.assertIn(r2, predicate_grd.get_triggered_rules(r1))


if __name__ == "__main__":
    unittest.main()
