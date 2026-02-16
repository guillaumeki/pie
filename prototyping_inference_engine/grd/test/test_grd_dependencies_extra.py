import unittest

from prototyping_inference_engine.grd.dependency_checker import DependencyChecker
from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class AllowAllChecker(DependencyChecker):
    def is_valid_positive_dependency(self, r1, r2, unifier) -> bool:
        return True

    def is_valid_negative_dependency(self, r1, r2, unifier) -> bool:
        return True


class TestGRDDependenciesExtra(unittest.TestCase):
    def test_triggered_prevented_and_ancestors(self) -> None:
        rules = list(
            DlgpeParser.instance().parse_rules(
                """
                q(X) :- p(X).
                r(X) :- q(X).
                s(X) :- r(X), not q(X).
                """
            )
        )
        r1, r2, r3 = rules
        grd = GRD(rules, checkers=[AllowAllChecker()])

        self.assertEqual({r2}, grd.get_triggered_rules(r1))
        self.assertEqual({r3}, grd.get_prevented_rules(r1))

        ancestors = grd.get_ancestor_rules(r3)
        self.assertEqual({r1, r2, r3}, ancestors)

        edges = list(grd.iter_edges())
        positives = [edge for edge in edges if edge.is_positive]
        negatives = [edge for edge in edges if not edge.is_positive]
        self.assertEqual(2, len(positives))
        self.assertEqual(1, len(negatives))


if __name__ == "__main__":
    unittest.main()
