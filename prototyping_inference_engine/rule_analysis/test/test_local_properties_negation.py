import unittest

from prototyping_inference_engine.rule_analysis.analyser import RuleAnalyser
from prototyping_inference_engine.rule_analysis.model import PropertyId, PropertyStatus
from prototyping_inference_engine.rule_analysis.test._helpers import parse_rules


class TestLocalPropertiesNegation(unittest.TestCase):
    def test_linear_counts_positive_body_atoms_with_safe_negation(self):
        analyser = RuleAnalyser(parse_rules("q(X) :- p(X), not r(X)."))

        report = analyser.analyse([PropertyId.LINEAR])

        self.assertEqual(report.get(PropertyId.LINEAR).status, PropertyStatus.SATISFIED)

    def test_guarded_accepts_safe_negation_when_positive_guard_exists(self):
        analyser = RuleAnalyser(parse_rules("q(X) :- p(X, Y), not r(Y)."))

        report = analyser.analyse([PropertyId.GUARDED])

        self.assertEqual(
            report.get(PropertyId.GUARDED).status,
            PropertyStatus.SATISFIED,
        )

    def test_guarded_uses_negative_variables_in_coverage_check(self):
        analyser = RuleAnalyser(parse_rules("q(X) :- p(X), s(Y), not r(X, Y)."))

        report = analyser.analyse([PropertyId.GUARDED])

        self.assertEqual(report.get(PropertyId.GUARDED).status, PropertyStatus.VIOLATED)

    def test_frontier_guarded_accepts_safe_negation(self):
        analyser = RuleAnalyser(parse_rules("q(X) :- p(X, Y), not r(Y)."))

        report = analyser.analyse([PropertyId.FRONTIER_GUARDED])

        self.assertEqual(
            report.get(PropertyId.FRONTIER_GUARDED).status,
            PropertyStatus.SATISFIED,
        )

    def test_frontier_guarded_rejects_missing_positive_frontier_guard(self):
        analyser = RuleAnalyser(parse_rules("q(X, Y) :- p(X), s(Y), not r(X, Y)."))

        report = analyser.analyse([PropertyId.FRONTIER_GUARDED])

        self.assertEqual(
            report.get(PropertyId.FRONTIER_GUARDED).status,
            PropertyStatus.VIOLATED,
        )


if __name__ == "__main__":
    unittest.main()
