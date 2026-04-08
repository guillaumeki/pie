import unittest

from prototyping_inference_engine.rule_analysis.analyser import RuleAnalyser
from prototyping_inference_engine.rule_analysis.model import PropertyId, PropertyStatus
from prototyping_inference_engine.rule_analysis.test._helpers import parse_rules


class TestRuleAnalyser(unittest.TestCase):
    def test_linear_implies_guarded_and_frontier_guarded(self):
        analyser = RuleAnalyser(parse_rules("q(X) :- p(X)."))

        report = analyser.analyse()

        self.assertEqual(report.get(PropertyId.LINEAR).status, PropertyStatus.SATISFIED)
        self.assertEqual(
            report.get(PropertyId.GUARDED).status, PropertyStatus.SATISFIED
        )
        self.assertEqual(
            report.get(PropertyId.FRONTIER_GUARDED).status,
            PropertyStatus.SATISFIED,
        )

    def test_frontier_guarded_without_being_guarded(self):
        analyser = RuleAnalyser(parse_rules("t(X) :- p(X, Y), q(X, Z)."))

        report = analyser.analyse([PropertyId.GUARDED, PropertyId.FRONTIER_GUARDED])

        self.assertEqual(report.get(PropertyId.GUARDED).status, PropertyStatus.VIOLATED)
        self.assertEqual(
            report.get(PropertyId.FRONTIER_GUARDED).status,
            PropertyStatus.SATISFIED,
        )

    def test_range_restricted_detects_existential_head_variables(self):
        analyser = RuleAnalyser(parse_rules("q(X, Y) :- p(X)."))

        report = analyser.analyse([PropertyId.RANGE_RESTRICTED])

        self.assertEqual(
            report.get(PropertyId.RANGE_RESTRICTED).status,
            PropertyStatus.VIOLATED,
        )

    def test_sticky_and_weakly_sticky_split(self):
        analyser = RuleAnalyser(
            parse_rules(
                """
                q(X, Y) :- p(X).
                r(X) :- q(X, Y), s(Y).
                """
            )
        )

        report = analyser.analyse([PropertyId.STICKY, PropertyId.WEAKLY_STICKY])

        self.assertEqual(report.get(PropertyId.STICKY).status, PropertyStatus.VIOLATED)
        self.assertEqual(
            report.get(PropertyId.WEAKLY_STICKY).status,
            PropertyStatus.SATISFIED,
        )

    def test_weakly_sticky_negative_case(self):
        analyser = RuleAnalyser(
            parse_rules(
                """
                q(X, Y) :- p(X).
                p(Y) :- q(X, Y).
                r(X) :- q(X, Y), p(Y).
                """
            )
        )

        report = analyser.analyse([PropertyId.WEAKLY_STICKY])

        self.assertEqual(
            report.get(PropertyId.WEAKLY_STICKY).status,
            PropertyStatus.VIOLATED,
        )

    def test_negation_is_marked_unsupported_in_v1(self):
        analyser = RuleAnalyser(parse_rules("q(X) :- p(X), not r(X)."))

        report = analyser.analyse([PropertyId.GUARDED])

        self.assertEqual(
            report.get(PropertyId.GUARDED).status,
            PropertyStatus.UNSUPPORTED,
        )

    def test_disjunctive_head_is_marked_unsupported_in_v1(self):
        analyser = RuleAnalyser(parse_rules("q(X) | r(X) :- p(X)."))

        report = analyser.analyse([PropertyId.WEAKLY_ACYCLIC])

        self.assertEqual(
            report.get(PropertyId.WEAKLY_ACYCLIC).status,
            PropertyStatus.UNSUPPORTED,
        )

    def test_snapshot_sccs_follow_grd_components(self):
        analyser = RuleAnalyser(
            parse_rules(
                """
                q(X) :- p(X).
                p(X) :- q(X).
                t(X) :- s(X).
                """
            )
        )

        scc_labels = tuple(len(component) for component in analyser.snapshot.sccs)
        self.assertEqual(tuple(sorted(scc_labels)), (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
