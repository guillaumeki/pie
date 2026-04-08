import unittest

from prototyping_inference_engine.rule_analysis.analyser import RuleAnalyser
from prototyping_inference_engine.rule_analysis.model import PropertyId, PropertyStatus
from prototyping_inference_engine.rule_analysis.test._helpers import parse_rules


class TestLocalPropertiesDisjunction(unittest.TestCase):
    def test_linear_accepts_disjunctive_heads(self):
        analyser = RuleAnalyser(parse_rules("q(X) | r(X) :- p(X)."))

        report = analyser.analyse([PropertyId.LINEAR])

        self.assertEqual(report.get(PropertyId.LINEAR).status, PropertyStatus.SATISFIED)

    def test_guarded_accepts_disjunctive_heads(self):
        analyser = RuleAnalyser(parse_rules("q(X, Y) | r(X) :- p(X, Y)."))

        report = analyser.analyse([PropertyId.GUARDED])

        self.assertEqual(
            report.get(PropertyId.GUARDED).status,
            PropertyStatus.SATISFIED,
        )

    def test_frontier_guarded_accepts_disjunctive_heads(self):
        analyser = RuleAnalyser(parse_rules("u(X) | v(X) :- p(X, Y), q(X, Z)."))

        report = analyser.analyse([PropertyId.GUARDED, PropertyId.FRONTIER_GUARDED])

        self.assertEqual(report.get(PropertyId.GUARDED).status, PropertyStatus.VIOLATED)
        self.assertEqual(
            report.get(PropertyId.FRONTIER_GUARDED).status,
            PropertyStatus.SATISFIED,
        )

    def test_range_restricted_accepts_disjunction_and_safe_negation(self):
        analyser = RuleAnalyser(parse_rules("q(X) | r(X) :- p(X), not s(X)."))

        report = analyser.analyse([PropertyId.RANGE_RESTRICTED])

        self.assertEqual(
            report.get(PropertyId.RANGE_RESTRICTED).status,
            PropertyStatus.SATISFIED,
        )


if __name__ == "__main__":
    unittest.main()
