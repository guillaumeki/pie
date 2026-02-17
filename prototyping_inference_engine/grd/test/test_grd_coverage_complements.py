import unittest
from unittest.mock import patch

from prototyping_inference_engine.grd.grd import GRD, DependencyComputationMode
from prototyping_inference_engine.grd.grd import _conjunctive_head_rule
from prototyping_inference_engine.grd.stratification import (
    HybridPredicateUnifierStratification,
    MinimalEvaluationStratification,
    SingleEvaluationStratification,
    _scc_sort_key,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestGrdCoverageComplements(unittest.TestCase):
    def test_get_ancestor_rules_and_hybrid_cross_component_edges(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                [r1] q(X) :- p(X), r(X).
                [r2] p(X) :- q(X).
                [r3] t(X) :- q(X).
                """
            )
        )
        r1, r2, r3 = rules

        grd = GRD(rules, mode=DependencyComputationMode.HYBRID)
        self.assertIn(r3, grd.get_triggered_rules(r1))

        ancestors = grd.get_ancestor_rules(r3)
        self.assertIn(r3, ancestors)
        self.assertIn(r1, ancestors)

    def test_get_ancestor_rules_with_cycle(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                [a] q(X) :- p(X).
                [b] p(X) :- q(X).
                """
            )
        )
        a, b = rules
        grd = GRD(rules, mode=DependencyComputationMode.PREDICATE)
        ancestors = grd.get_ancestor_rules(a)
        self.assertEqual({a, b}, ancestors)

    def test_predicate_mode_negative_edge(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(X) :- p(X).
                s(X) :- p(X), not q(X).
                """
            )
        )
        r1, r2 = rules
        grd = GRD(rules, mode=DependencyComputationMode.PREDICATE)
        self.assertIn(r2, grd.get_prevented_rules(r1))

    def test_conjunctive_head_rule_with_empty_positive_body(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(a) :- not p(a).
                """
            )
        )
        (rule,) = rules
        head_rule = rule.extract_conjunctive_rule(rule, 0)
        result = _conjunctive_head_rule(head_rule, rule)
        self.assertIs(result, head_rule)

    def test_single_and_minimal_evaluation_stratification(self):
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(X) :- p(X).
                r(X) :- q(X).
                s(X) :- r(X).
                """
            )
        )
        grd = GRD(rules)

        single = grd.stratify(SingleEvaluationStratification())
        minimal_eval = grd.stratify(MinimalEvaluationStratification())

        self.assertIsNotNone(single)
        self.assertIsNotNone(minimal_eval)
        self.assertEqual(len(single or []), 3)
        self.assertEqual(len(minimal_eval or []), 3)

    def test_hybrid_stratification_defensive_none_branch(self):
        rules = list(DlgpeParser.instance().parse_rules("q(X) :- p(X)."))
        grd = GRD(rules)
        strategy = HybridPredicateUnifierStratification()

        with patch(
            "prototyping_inference_engine.grd.stratification.BySccStratification.compute",
            return_value=None,
        ):
            self.assertIsNone(strategy.compute(grd))

    def test_scc_sort_key_empty(self):
        self.assertEqual(_scc_sort_key([]), "")


if __name__ == "__main__":
    unittest.main()
