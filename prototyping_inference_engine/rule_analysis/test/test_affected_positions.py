import unittest

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot
from prototyping_inference_engine.rule_analysis.test._helpers import parse_rules


class TestAffectedPositions(unittest.TestCase):
    def test_direct_and_propagated_affected_positions(self):
        rules = parse_rules(
            """
            q(X, Y) :- p(X).
            r(X, Y, Z) :- q(X, Y).
            """
        )

        snapshot = AnalysisSnapshot(rules)
        affected = snapshot.affected_positions

        self.assertTrue(affected.contains(Predicate("q", 2), 1))
        self.assertTrue(affected.contains(Predicate("r", 3), 1))
        self.assertTrue(affected.contains(Predicate("r", 3), 2))
        self.assertFalse(affected.contains(Predicate("r", 3), 0))


if __name__ == "__main__":
    unittest.main()
