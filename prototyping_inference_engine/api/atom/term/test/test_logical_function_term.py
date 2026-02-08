from unittest import TestCase

from prototyping_inference_engine.api.atom.term.logical_function_term import (
    LogicalFunctionalTerm,
)
from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.api.atom.term.constant import Constant


class TestFunctionalTerms(TestCase):
    def test_logical_function_term_ground(self):
        term = LogicalFunctionalTerm("f", [Constant("a")])
        self.assertTrue(term.is_ground)

    def test_evaluable_function_term_ground(self):
        term = EvaluableFunctionTerm("stdfct:sum", [Constant("1"), Constant("2")])
        self.assertTrue(term.is_ground)
