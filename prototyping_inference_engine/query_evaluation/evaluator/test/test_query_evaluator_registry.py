"""Tests for QueryEvaluatorRegistry with FOQuery dispatch."""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator_registry import (
    QueryEvaluatorRegistry,
)


class TestFOQueryViaRegistry(unittest.TestCase):
    """Test FOQuery evaluation via the query registry."""

    def setUp(self):
        QueryEvaluatorRegistry.reset()
        self.registry = QueryEvaluatorRegistry.instance()

        self.p = Predicate("p", 1)
        self.x = Variable("X")
        self.a = Constant("a")
        self.b = Constant("b")

    def tearDown(self):
        QueryEvaluatorRegistry.reset()

    def test_get_evaluator_for_fo_query(self):
        """Registry returns the FOQuery evaluator."""
        foq = FOQuery(Atom(self.p, self.x), [self.x])

        evaluator = self.registry.get_evaluator(foq)

        self.assertIsNotNone(evaluator)
        self.assertIsInstance(evaluator, GenericFOQueryEvaluator)

    def test_evaluate_via_registry(self):
        """Evaluating an FOQuery via registry returns expected results."""
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a),
                Atom(self.p, self.b),
            ]
        )
        foq = FOQuery(Atom(self.p, self.x), [self.x])

        evaluator = self.registry.get_evaluator(foq)
        results = list(evaluator.evaluate(foq, fact_base))

        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
