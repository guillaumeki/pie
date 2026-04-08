import unittest

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.rule_analysis.model import PredicatePosition
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

    def test_disjunctive_heads_contribute_edges_for_all_disjuncts(self):
        rules = parse_rules("q(X, Y) | s(X, Z) :- p(X).")

        snapshot = AnalysisSnapshot(rules)
        graph = snapshot.position_dependency_graph

        source = PredicatePosition(Predicate("p", 1), 0)
        first_target = PredicatePosition(Predicate("q", 2), 0)
        second_target = PredicatePosition(Predicate("s", 2), 0)

        observed_edges = {
            (edge.source, edge.target, edge.is_special) for edge in graph.edges
        }
        self.assertIn((source, first_target, False), observed_edges)
        self.assertIn((source, second_target, False), observed_edges)


if __name__ == "__main__":
    unittest.main()
