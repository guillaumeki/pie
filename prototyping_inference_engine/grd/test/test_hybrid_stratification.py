import unittest

from prototyping_inference_engine.grd.grd import (
    GRD,
    DependencyComputationMode,
)
from prototyping_inference_engine.grd.stratification import (
    BySccStratification,
    HybridPredicateUnifierStratification,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


def _normalize(strata):
    return {frozenset(rb.rules) for rb in strata}


class TestHybridStratification(unittest.TestCase):
    def test_hybrid_matches_unifier_scc_partition(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                [r1] q(X) :- p(X).
                [r2] p(X) :- q(X).
                [r3] s(X) :- r(X).
                [r4] r(X) :- s(X).
                [r5] t(X) :- q(X).
                """
            )
        )

        unifier_grd = GRD(rules, mode=DependencyComputationMode.UNIFIER)
        hybrid_strategy = HybridPredicateUnifierStratification()

        baseline = unifier_grd.stratify(BySccStratification())
        hybrid = unifier_grd.stratify(hybrid_strategy)

        self.assertIsNotNone(baseline)
        self.assertIsNotNone(hybrid)
        self.assertEqual(_normalize(baseline or []), _normalize(hybrid or []))
        self.assertGreaterEqual(hybrid_strategy.last_stats["coarse_blocks"], 2)
        self.assertLess(
            hybrid_strategy.last_stats["refined_candidate_pairs"],
            hybrid_strategy.last_stats["full_candidate_pairs"],
        )

    def test_hybrid_grd_mode_runs(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                [a] q(X) :- p(X).
                [b] p(X) :- q(X).
                [c] r(X) :- s(X).
                """
            )
        )
        grd = GRD(rules, mode=DependencyComputationMode.HYBRID)
        self.assertEqual(grd.mode, DependencyComputationMode.HYBRID)
        self.assertEqual(len(grd.rules), 3)


if __name__ == "__main__":
    unittest.main()
