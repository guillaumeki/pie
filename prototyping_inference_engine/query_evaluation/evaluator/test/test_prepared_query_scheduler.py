"""Tests for prepared query scheduling."""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.atomic_pattern import UnconstrainedPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    ConjunctiveFOQueryEvaluator,
)


class _TracingData(ReadableData):
    def __init__(self, facts, bounds):
        self._facts = facts
        self._bounds = bounds
        self.log = []

    def get_predicates(self):
        return iter(self._facts.keys())

    def has_predicate(self, predicate):
        return predicate in self._facts

    def get_atomic_pattern(self, predicate):
        return UnconstrainedPattern(predicate)

    def evaluate(self, query: BasicQuery):
        self.log.append(query.predicate)
        results = []
        for value in self._facts.get(query.predicate, []):
            if query.bound_positions:
                bound = query.get_bound_term(0)
                if bound is not None and bound != value:
                    continue
            results.append((value,))
        return iter(results)

    def can_evaluate(self, query: BasicQuery):
        return query.predicate in self._facts

    def estimate_bound(self, query: BasicQuery):
        return self._bounds.get(query.predicate)


class TestPreparedScheduler(unittest.TestCase):
    def test_scheduler_uses_smallest_bound_first(self):
        x = Variable("X")
        p = Predicate("p", 1)
        q = Predicate("q", 1)

        facts = {
            p: [Constant("a"), Constant("b")],
            q: [Constant("a")],
        }
        bounds = {p: 10, q: 1}
        data = _TracingData(facts, bounds)

        formula = ConjunctionFormula(Atom(p, x), Atom(q, x))
        query = FOQuery(formula, [x])

        evaluator = ConjunctiveFOQueryEvaluator()
        results = list(evaluator.evaluate(query, data, Substitution()))

        self.assertEqual(data.log[0], q)
        self.assertEqual(results, [Substitution({x: Constant("a")})])


if __name__ == "__main__":
    unittest.main()
