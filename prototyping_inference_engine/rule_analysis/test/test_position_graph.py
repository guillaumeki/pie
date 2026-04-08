import unittest

from prototyping_inference_engine.rule_analysis.snapshot import AnalysisSnapshot
from prototyping_inference_engine.rule_analysis.test._helpers import parse_rules


class TestPositionDependencyGraph(unittest.TestCase):
    def test_weakly_acyclic_ruleset(self):
        rules = parse_rules("r(X, Y) :- p(X).")

        snapshot = AnalysisSnapshot(rules)

        self.assertTrue(snapshot.position_dependency_graph.is_weakly_acyclic())

    def test_special_cycle_breaks_weak_acyclicity(self):
        rules = parse_rules(
            """
            r(X, Y) :- p(X).
            p(Y) :- r(X, Y).
            """
        )

        snapshot = AnalysisSnapshot(rules)

        self.assertFalse(snapshot.position_dependency_graph.is_weakly_acyclic())
        self.assertTrue(snapshot.position_dependency_graph.non_finite_rank_positions)


if __name__ == "__main__":
    unittest.main()
