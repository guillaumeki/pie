import unittest

from prototyping_inference_engine.rule_analysis.analyser import RuleAnalyser
from prototyping_inference_engine.rule_analysis.model import PropertyId, PropertyStatus
from prototyping_inference_engine.rule_analysis.test._helpers import parse_rules


class TestStickyFragmentBoundaries(unittest.TestCase):
    def test_sticky_rejects_disjunctive_heads(self):
        analyser = RuleAnalyser(parse_rules("q(X) | r(X, Y) :- p(X)."))

        report = analyser.analyse([PropertyId.STICKY, PropertyId.WEAKLY_STICKY])

        self.assertEqual(report.get(PropertyId.STICKY).status, PropertyStatus.VIOLATED)
        self.assertEqual(
            report.get(PropertyId.STICKY).evidence,
            ("disjunctive_head",),
        )
        self.assertEqual(
            report.get(PropertyId.WEAKLY_STICKY).status,
            PropertyStatus.VIOLATED,
        )
        self.assertEqual(
            report.get(PropertyId.WEAKLY_STICKY).evidence,
            ("disjunctive_head",),
        )

    def test_sticky_rejects_negation(self):
        analyser = RuleAnalyser(parse_rules("q(X) :- p(X), not r(X)."))

        report = analyser.analyse([PropertyId.STICKY])

        self.assertEqual(report.get(PropertyId.STICKY).status, PropertyStatus.VIOLATED)
        self.assertEqual(report.get(PropertyId.STICKY).evidence, ("negation",))


if __name__ == "__main__":
    unittest.main()
