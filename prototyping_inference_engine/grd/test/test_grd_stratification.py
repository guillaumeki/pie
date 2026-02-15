import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.grd.stratification import (
    BySccStratification,
    MinimalEvaluationStratification,
    MinimalStratification,
    SingleEvaluationStratification,
)


class TestGrdStratification(unittest.TestCase):
    def setUp(self) -> None:
        self.x = Variable("X")
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.r = Predicate("r", 1)
        self.s = Predicate("s", 1)
        self.t = Predicate("t", 1)

    def _atom(self, pred: Predicate) -> Atom:
        return Atom(pred, self.x)

    def _rule(self, body, head, label: str) -> Rule:
        return Rule(body, head, label=label)

    def test_by_scc_stratification_order(self) -> None:
        r1 = self._rule(self._atom(self.p), self._atom(self.q), label="r1")
        r2 = self._rule(self._atom(self.q), self._atom(self.r), label="r2")
        r3 = self._rule(self._atom(self.r), self._atom(self.t), label="r3")

        grd = GRD([r1, r2, r3])
        strata = grd.stratify(BySccStratification())

        self.assertIsNotNone(strata)
        strates = strata or []
        self.assertEqual(3, len(strates))
        self.assertEqual({r1}, strates[0].rules)
        self.assertEqual({r2}, strates[1].rules)
        self.assertEqual({r3}, strates[2].rules)

    def test_is_stratifiable_with_negative_cycle(self) -> None:
        r1 = self._rule(self._atom(self.p), self._atom(self.q), label="r1")
        r2_body = ConjunctionFormula(
            self._atom(self.q), NegationFormula(self._atom(self.s))
        )
        r2 = self._rule(r2_body, self._atom(self.r), label="r2")
        r3 = self._rule(self._atom(self.r), self._atom(self.s), label="r3")

        grd = GRD([r1, r2, r3])
        self.assertFalse(grd.is_stratifiable())

    def test_minimal_stratification(self) -> None:
        r1 = self._rule(self._atom(self.p), self._atom(self.q), label="r1")
        r2_body = ConjunctionFormula(
            self._atom(self.q), NegationFormula(self._atom(self.s))
        )
        r2 = self._rule(r2_body, self._atom(self.r), label="r2")
        r3 = self._rule(self._atom(self.s), self._atom(self.t), label="r3")

        grd = GRD([r1, r2, r3])
        strata = grd.stratify(MinimalStratification())

        self.assertIsNotNone(strata)
        strates = strata or []
        self.assertEqual(2, len(strates))
        self.assertEqual({r1, r3}, strates[0].rules)
        self.assertEqual({r2}, strates[1].rules)

    def test_single_evaluation_stratification(self) -> None:
        r1 = self._rule(self._atom(self.p), self._atom(self.q), label="r1")
        r2 = self._rule(self._atom(self.q), self._atom(self.r), label="r2")
        r3 = self._rule(self._atom(self.r), self._atom(self.t), label="r3")

        grd = GRD([r1, r2, r3])
        strata = grd.stratify(SingleEvaluationStratification())

        self.assertIsNotNone(strata)
        strates = strata or []
        self.assertEqual(3, len(strates))
        self.assertEqual({r1}, strates[0].rules)
        self.assertEqual({r2}, strates[1].rules)
        self.assertEqual({r3}, strates[2].rules)

    def test_minimal_evaluation_stratification_acyclic(self) -> None:
        r1 = self._rule(self._atom(self.p), self._atom(self.q), label="r1")
        r2 = self._rule(self._atom(self.q), self._atom(self.r), label="r2")
        r3 = self._rule(self._atom(self.s), self._atom(self.t), label="r3")

        grd = GRD([r1, r2, r3])
        strata = grd.stratify(MinimalEvaluationStratification())

        self.assertIsNotNone(strata)
        strates = strata or []
        self.assertEqual(2, len(strates))
        self.assertEqual({r1, r3}, strates[0].rules)
        self.assertEqual({r2}, strates[1].rules)

    def test_minimal_evaluation_stratification_cycle(self) -> None:
        r1 = self._rule(self._atom(self.p), self._atom(self.q), label="r1")
        r2 = self._rule(self._atom(self.q), self._atom(self.p), label="r2")
        r3 = self._rule(self._atom(self.p), self._atom(self.r), label="r3")

        grd = GRD([r1, r2, r3])
        strata = grd.stratify(MinimalEvaluationStratification())

        self.assertIsNotNone(strata)
        strates = strata or []
        self.assertEqual(2, len(strates))
        self.assertEqual({r1, r2}, strates[0].rules)
        self.assertEqual({r3}, strates[1].rules)
