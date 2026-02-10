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
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.negation_formula import (
    NegationFormula,
)
from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
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


class _FunctionSchedulerData(ReadableData):
    def __init__(self, p_predicate, s_predicate, sum_predicate, one, two, three):
        self._p_predicate = p_predicate
        self._s_predicate = s_predicate
        self._sum_predicate = sum_predicate
        self._one = one
        self._two = two
        self._three = three
        self.log = []

    def get_predicates(self):
        return iter([self._p_predicate, self._s_predicate, self._sum_predicate])

    def has_predicate(self, predicate):
        return predicate in {
            self._p_predicate,
            self._s_predicate,
            self._sum_predicate,
        }

    def get_atomic_pattern(self, predicate):
        return UnconstrainedPattern(predicate)

    def can_evaluate(self, query: BasicQuery):
        bound = set(query.bound_positions.keys())
        if query.predicate == self._p_predicate:
            return True
        if query.predicate == self._sum_predicate:
            return {0, 1}.issubset(bound)
        if query.predicate == self._s_predicate:
            return 0 in bound
        return False

    def estimate_bound(self, query: BasicQuery):
        if not self.can_evaluate(query):
            return None
        return 1

    def evaluate(self, query: BasicQuery):
        self.log.append(query.predicate)
        if query.predicate == self._p_predicate:
            return iter([(self._one, self._two)])
        if query.predicate == self._sum_predicate:
            if (
                query.get_bound_term(0) == self._one
                and query.get_bound_term(1) == self._two
            ):
                return iter([(self._three,)])
            return iter(())
        if query.predicate == self._s_predicate:
            if query.get_bound_term(0) == self._three:
                return iter([()])
            return iter(())
        return iter(())


class _SubstitutionSchedulerData(ReadableData):
    def __init__(self, p_predicate, q_predicate, r_predicate, value):
        self._p_predicate = p_predicate
        self._q_predicate = q_predicate
        self._r_predicate = r_predicate
        self._value = value
        self.log = []

    def get_predicates(self):
        return iter([self._p_predicate, self._q_predicate, self._r_predicate])

    def has_predicate(self, predicate):
        return predicate in {
            self._p_predicate,
            self._q_predicate,
            self._r_predicate,
        }

    def get_atomic_pattern(self, predicate):
        return UnconstrainedPattern(predicate)

    def can_evaluate(self, query: BasicQuery):
        bound = set(query.bound_positions.keys())
        if query.predicate == self._p_predicate:
            return True
        if query.predicate in {self._q_predicate, self._r_predicate}:
            return 0 in bound
        return False

    def estimate_bound(self, query: BasicQuery):
        if not self.can_evaluate(query):
            return None
        if query.predicate == self._r_predicate:
            return 1
        if query.predicate == self._q_predicate:
            return 5
        return 10

    def evaluate(self, query: BasicQuery):
        self.log.append(query.predicate)
        if query.predicate == self._p_predicate:
            return iter([(self._value,)])
        if query.predicate in {self._q_predicate, self._r_predicate}:
            if query.get_bound_term(0) == self._value:
                return iter([()])
            return iter(())
        return iter(())


class _NegationFunctionSchedulerData(ReadableData):
    def __init__(
        self, p_predicate, s_predicate, sum_predicate, q_predicate, one, two, three
    ):
        self._p_predicate = p_predicate
        self._s_predicate = s_predicate
        self._sum_predicate = sum_predicate
        self._q_predicate = q_predicate
        self._one = one
        self._two = two
        self._three = three
        self.log = []

    def get_predicates(self):
        return iter(
            [
                self._p_predicate,
                self._s_predicate,
                self._sum_predicate,
                self._q_predicate,
            ]
        )

    def has_predicate(self, predicate):
        return predicate in {
            self._p_predicate,
            self._s_predicate,
            self._sum_predicate,
            self._q_predicate,
        }

    def get_atomic_pattern(self, predicate):
        return UnconstrainedPattern(predicate)

    def can_evaluate(self, query: BasicQuery):
        bound = set(query.bound_positions.keys())
        if query.predicate == self._p_predicate:
            return True
        if query.predicate == self._sum_predicate:
            return {0, 1}.issubset(bound)
        if query.predicate == self._s_predicate:
            return 0 in bound
        if query.predicate == self._q_predicate:
            return 0 in bound
        return False

    def estimate_bound(self, query: BasicQuery):
        if not self.can_evaluate(query):
            return None
        return 1

    def evaluate(self, query: BasicQuery):
        self.log.append(query.predicate)
        if query.predicate == self._p_predicate:
            return iter([(self._one, self._two)])
        if query.predicate == self._sum_predicate:
            if (
                query.get_bound_term(0) == self._one
                and query.get_bound_term(1) == self._two
            ):
                return iter([(self._three,)])
            return iter(())
        if query.predicate == self._s_predicate:
            if query.get_bound_term(0) == self._three:
                return iter([()])
            return iter(())
        if query.predicate == self._q_predicate:
            return iter(())
        return iter(())


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

        evaluator = GenericFOQueryEvaluator()
        results = list(evaluator.evaluate(query, data, Substitution()))

        self.assertEqual(data.log[0], q)
        self.assertEqual(results, [Substitution({x: Constant("a")})])

    def test_scheduler_defers_function_terms_until_evaluable(self):
        x = Variable("X")
        y = Variable("Y")
        p = Predicate("p", 2)
        s = Predicate("s", 1)
        sum_predicate = Predicate("stdfct:sum", 3)
        one = Constant("1")
        two = Constant("2")
        three = Constant("3")

        data = _FunctionSchedulerData(p, s, sum_predicate, one, two, three)
        formula = ConjunctionFormula(
            Atom(s, EvaluableFunctionTerm("stdfct:sum", [x, y])),
            Atom(p, x, y),
        )
        quantified = ExistentialFormula(x, ExistentialFormula(y, formula))
        query = FOQuery(quantified, [])

        evaluator = GenericFOQueryEvaluator()
        results = list(evaluator.evaluate(query, data, Substitution()))

        self.assertEqual(len(results), 1)
        self.assertEqual(data.log[0], p)
        self.assertEqual(data.log[1], sum_predicate)
        self.assertEqual(data.log[2], s)

    def test_scheduler_reorders_after_substitution_updates(self):
        x = Variable("X")
        p = Predicate("p", 1)
        q = Predicate("q", 1)
        r = Predicate("r", 1)
        value = Constant("a")

        data = _SubstitutionSchedulerData(p, q, r, value)
        formula = ConjunctionFormula(
            Atom(p, x),
            ConjunctionFormula(Atom(q, x), Atom(r, x)),
        )
        formula = ExistentialFormula(x, formula)
        query = FOQuery(formula, [])

        evaluator = GenericFOQueryEvaluator()
        results = list(evaluator.evaluate(query, data, Substitution()))

        self.assertEqual(len(results), 1)
        self.assertEqual(data.log[0], p)
        self.assertEqual(data.log[1], r)
        self.assertEqual(data.log[2], q)

    def test_scheduler_defers_negation_until_safe(self):
        x = Variable("X")
        y = Variable("Y")
        p = Predicate("p", 2)
        s = Predicate("s", 1)
        sum_predicate = Predicate("stdfct:sum", 3)
        q = Predicate("q", 1)
        one = Constant("1")
        two = Constant("2")
        three = Constant("3")

        data = _NegationFunctionSchedulerData(p, s, sum_predicate, q, one, two, three)
        formula = ConjunctionFormula(
            Atom(p, x, y),
            ConjunctionFormula(
                Atom(s, EvaluableFunctionTerm("stdfct:sum", [x, y])),
                NegationFormula(Atom(q, x)),
            ),
        )
        formula = ExistentialFormula(x, ExistentialFormula(y, formula))
        query = FOQuery(formula, [])

        evaluator = GenericFOQueryEvaluator()
        results = list(evaluator.evaluate(query, data, Substitution()))

        self.assertEqual(len(results), 1)
        self.assertEqual(data.log[0], p)
        self.assertEqual(data.log[-1], q)


if __name__ == "__main__":
    unittest.main()
