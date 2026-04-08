import unittest

from prototyping_inference_engine.rule_analysis.analyser import RuleAnalyser
from prototyping_inference_engine.rule_analysis.model import PropertyId, PropertyStatus
from prototyping_inference_engine.rule_analysis.test._helpers import parse_rules


class TestWeaklyAcyclicDisjunction(unittest.TestCase):
    def test_disjunctive_ruleset_can_be_weakly_acyclic(self):
        analyser = RuleAnalyser(parse_rules("q(X, Y) | s(X, Z) :- p(X)."))

        report = analyser.analyse([PropertyId.WEAKLY_ACYCLIC])

        self.assertEqual(
            report.get(PropertyId.WEAKLY_ACYCLIC).status,
            PropertyStatus.SATISFIED,
        )

    def test_disjunctive_ruleset_can_break_weak_acyclicity(self):
        analyser = RuleAnalyser(
            parse_rules(
                """
                q(X, Y) | s(X, Z) :- p(X).
                p(Y) :- q(X, Y).
                """
            )
        )

        report = analyser.analyse([PropertyId.WEAKLY_ACYCLIC])

        self.assertEqual(
            report.get(PropertyId.WEAKLY_ACYCLIC).status,
            PropertyStatus.VIOLATED,
        )


if __name__ == "__main__":
    unittest.main()
