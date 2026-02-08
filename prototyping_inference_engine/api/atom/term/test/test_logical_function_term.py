from unittest import TestCase

from prototyping_inference_engine.api.atom.term.logical_function_term import (
    LogicalFunctionalTerm,
)
from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestFunctionalTerms(TestCase):
    def test_logical_function_term_ground(self):
        term = LogicalFunctionalTerm("f", [Constant("a")])
        self.assertTrue(term.is_ground)

    def test_evaluable_function_term_ground(self):
        term = EvaluableFunctionTerm("stdfct:sum", [Constant("1"), Constant("2")])
        self.assertTrue(term.is_ground)

    def test_logical_function_term_apply_substitution(self):
        term = LogicalFunctionalTerm("f", [Variable("X"), Constant("a")])
        substitution = Substitution({Variable("X"): Constant("b")})
        result = term.apply_substitution(substitution)
        self.assertEqual(result.args, (Constant("b"), Constant("a")))

    def test_evaluable_function_term_apply_substitution(self):
        term = EvaluableFunctionTerm("stdfct:sum", [Variable("X"), Constant("2")])
        substitution = Substitution({Variable("X"): Constant("1")})
        result = term.apply_substitution(substitution)
        self.assertEqual(result.args, (Constant("1"), Constant("2")))
