from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    AtomicFOQueryEvaluator,
)
from prototyping_inference_engine.rule_compilation.id.id_rule_compilation import (
    IDRuleCompilation,
)


class TestAtomicFOQueryEvaluatorCompilation(TestCase):
    def test_atomic_homomorphism_with_compilation(self):
        p = Predicate("p", 2)
        q = Predicate("q", 2)
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")

        query = FOQuery(Atom(q, x, y), [x, y])
        fact_base = FrozenInMemoryFactBase({Atom(p, a, b)})

        rule_base = RuleBase(
            {
                Rule(Atom(p, x, y), Atom(q, x, y)),
            }
        )
        compilation = IDRuleCompilation()
        compilation.compile(rule_base)

        evaluator = AtomicFOQueryEvaluator()
        results = set(
            frozenset(result.items())
            for result in evaluator.evaluate(
                query, fact_base, rule_compilation=compilation
            )
        )

        expected = {frozenset(Substitution({x: a, y: b}).items())}
        self.assertEqual(expected, results)

    def test_atomic_homomorphism_with_swapped_variables(self):
        p = Predicate("p", 2)
        q = Predicate("q", 2)
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")

        query = FOQuery(Atom(q, x, y), [x, y])
        fact_base = FrozenInMemoryFactBase({Atom(p, a, b)})

        rule_base = RuleBase(
            {
                Rule(Atom(p, x, y), Atom(q, y, x)),
            }
        )
        compilation = IDRuleCompilation()
        compilation.compile(rule_base)

        evaluator = AtomicFOQueryEvaluator()
        results = set(
            frozenset(result.items())
            for result in evaluator.evaluate(
                query, fact_base, rule_compilation=compilation
            )
        )

        expected = {frozenset(Substitution({x: b, y: a}).items())}
        self.assertEqual(expected, results)
