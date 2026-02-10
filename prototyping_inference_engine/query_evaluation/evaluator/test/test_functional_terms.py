"""Tests for logical functional terms in FOQuery evaluation."""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.logical_function_term import (
    LogicalFunctionalTerm,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
)


class TestFunctionalTermsInQueries(unittest.TestCase):
    """Validate matching with logical functional terms."""

    def setUp(self):
        self.evaluator = GenericFOQueryEvaluator()

    def test_match_with_functional_terms(self):
        """
        Query: ?() :- p(a,b,g(a))
        FactBase: {p(a,b,g(a)), p(a,b,f(a)), p(c,b,g(a))}
        Expected: one result
        """
        p = Predicate("p", 3)
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        term_g_a = LogicalFunctionalTerm("g", [a])
        term_f_a = LogicalFunctionalTerm("f", [a])

        facts = MutableInMemoryFactBase(
            [
                Atom(p, a, b, term_g_a),
                Atom(p, a, b, term_f_a),
                Atom(p, c, b, term_g_a),
            ]
        )

        query = FOQuery(Atom(p, a, b, term_g_a), [])
        results = list(self.evaluator.evaluate_and_project(query, facts))

        self.assertEqual(results, [()])

    def test_match_without_constants(self):
        """
        Query: ?() :- p(f(g(a)))
        FactBase: {p(f(g(a)))}
        Expected: one result
        """
        p = Predicate("p", 1)
        a = Constant("a")

        term_g_a = LogicalFunctionalTerm("g", [a])
        term_f_g_a = LogicalFunctionalTerm("f", [term_g_a])

        facts = MutableInMemoryFactBase([Atom(p, term_f_g_a)])

        query = FOQuery(Atom(p, term_f_g_a), [])
        results = list(self.evaluator.evaluate_and_project(query, facts))

        self.assertEqual(results, [()])

    def test_incoherent_conjunction_rejected(self):
        """
        Query: ?() :- p(f(g(a)))
        FactBase: {p(f(g(b)))}
        Expected: no results
        """
        p = Predicate("p", 1)
        a = Constant("a")
        b = Constant("b")

        term_query = LogicalFunctionalTerm("f", [LogicalFunctionalTerm("g", [a])])
        term_fact = LogicalFunctionalTerm("f", [LogicalFunctionalTerm("g", [b])])

        facts = MutableInMemoryFactBase([Atom(p, term_fact)])

        query = FOQuery(Atom(p, term_query), [])
        results = list(self.evaluator.evaluate_and_project(query, facts))

        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
