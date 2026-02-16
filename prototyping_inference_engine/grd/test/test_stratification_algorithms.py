import unittest

from prototyping_inference_engine.grd.stratification import (
    BySccStratification,
    Edge,
    MinimalEvaluationStratification,
    MinimalStratification,
    SingleEvaluationStratification,
    is_stratifiable,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class FakeGRD:
    def __init__(self, rules, edges):
        self._rules = tuple(rules)
        self._edges = list(edges)

    @property
    def rules(self):
        return self._rules

    def iter_edges(self):
        return iter(self._edges)


class TestStratificationAlgorithms(unittest.TestCase):
    def _rules_by_label(self, text):
        rules = list(DlgpeParser.instance().parse_rules(text))
        return {rule.label: rule for rule in rules}

    def test_is_stratifiable_false_on_negative_cycle(self) -> None:
        rules = self._rules_by_label(
            """
            [r1] p(X) :- q(X).
            [r2] q(X) :- p(X).
            """
        )
        r1, r2 = rules["r1"], rules["r2"]
        grd = FakeGRD(
            [r1, r2],
            [Edge(r1, r2, is_positive=False), Edge(r2, r1, is_positive=True)],
        )
        self.assertFalse(is_stratifiable(grd))

    def test_by_scc_stratification_orders_components(self) -> None:
        rules = self._rules_by_label(
            """
            [r1] p(X) :- q(X).
            [r2] q(X) :- r(X).
            [r3] r(X) :- q(X).
            """
        )
        r1, r2, r3 = rules["r1"], rules["r2"], rules["r3"]
        grd = FakeGRD(
            [r1, r2, r3],
            [Edge(r1, r2, True), Edge(r2, r3, True), Edge(r3, r2, True)],
        )
        strata = BySccStratification().compute(grd)
        self.assertIsNotNone(strata)
        label_sets = [set(rule.label for rule in rb.rules) for rb in strata or []]
        self.assertEqual([{"r1"}, {"r2", "r3"}], label_sets)

    def test_minimal_evaluation_groups_independent_scc(self) -> None:
        rules = self._rules_by_label(
            """
            [r1] p(X) :- q(X).
            [r2] q(X) :- r(X).
            [r3] s(X) :- t(X).
            """
        )
        r1, r2, r3 = rules["r1"], rules["r2"], rules["r3"]
        grd = FakeGRD([r1, r2, r3], [Edge(r1, r2, True)])
        strata = MinimalEvaluationStratification().compute(grd)
        self.assertIsNotNone(strata)
        label_sets = [set(rule.label for rule in rb.rules) for rb in strata or []]
        self.assertEqual([{"r1", "r3"}, {"r2"}], label_sets)

    def test_minimal_stratification_returns_none_on_negative_cycle(self) -> None:
        rules = self._rules_by_label(
            """
            [r1] p(X) :- q(X).
            [r2] q(X) :- p(X).
            """
        )
        r1, r2 = rules["r1"], rules["r2"]
        grd = FakeGRD(
            [r1, r2],
            [Edge(r1, r2, False), Edge(r2, r1, False)],
        )
        strata = MinimalStratification().compute(grd)
        self.assertIsNone(strata)

    def test_single_evaluation_returns_none_on_cycle(self) -> None:
        rules = self._rules_by_label(
            """
            [r1] p(X) :- q(X).
            [r2] q(X) :- p(X).
            """
        )
        r1, r2 = rules["r1"], rules["r2"]
        grd = FakeGRD([r1, r2], [Edge(r1, r2, True), Edge(r2, r1, True)])
        strata = SingleEvaluationStratification().compute(grd)
        self.assertIsNone(strata)


if __name__ == "__main__":
    unittest.main()
