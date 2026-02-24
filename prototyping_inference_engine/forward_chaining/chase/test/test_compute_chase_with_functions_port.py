"""Ported chase-with-functions integration tests."""

from __future__ import annotations

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.test.port_test_utils import (
    test_builder,
)


class TestComputeChaseWithFunctionsPort(unittest.TestCase):
    def test_functions_are_evaluated_during_chase(self) -> None:
        literal_factory = LiteralFactory(DictStorage())
        one = literal_factory.create("1")
        two = literal_factory.create("2")

        x = Variable("X")
        num = Predicate("num", 1)
        q_sum = Predicate("q_sum", 1)
        q_nested = Predicate("q_nested", 1)

        rule_sum = Rule(
            Atom(num, x), Atom(q_sum, EvaluableFunctionTerm("stdfct:sum", [x, one]))
        )
        rule_nested = Rule(
            Atom(num, x),
            Atom(
                q_nested,
                EvaluableFunctionTerm(
                    "stdfct:toInt", [EvaluableFunctionTerm("stdfct:sum", [x, one])]
                ),
            ),
        )

        fact_base = MutableInMemoryFactBase([Atom(num, two)])
        rule_base = RuleBase({rule_sum, rule_nested})

        chase = (
            test_builder(fact_base, rule_base).use_naive_rule_scheduler().build().get()
        )
        chase.execute()

        sum_terms = [a.terms[0] for a in fact_base if a.predicate == q_sum]
        nested_terms = [a.terms[0] for a in fact_base if a.predicate == q_nested]

        self.assertEqual(1, len(sum_terms))
        self.assertEqual(1, len(nested_terms))
        self.assertIsInstance(sum_terms[0], Literal)
        self.assertIsInstance(nested_terms[0], Literal)

        sum_lit = sum_terms[0]
        nested_lit = nested_terms[0]
        assert isinstance(sum_lit, Literal)
        assert isinstance(nested_lit, Literal)
        self.assertEqual(3, sum_lit.value)
        self.assertEqual(3, nested_lit.value)


if __name__ == "__main__":
    unittest.main()
