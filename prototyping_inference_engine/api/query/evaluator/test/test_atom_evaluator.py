"""
Tests for AtomEvaluator.
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.api.query.evaluator.atom_evaluator import AtomEvaluator
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestAtomEvaluator(unittest.TestCase):
    """Test AtomEvaluator."""

    def setUp(self):
        self.evaluator = AtomEvaluator()
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.a = Constant("a")
        self.b = Constant("b")
        self.c = Constant("c")

    def test_supported_formula_type(self):
        self.assertEqual(AtomEvaluator.supported_formula_type(), Atom)

    def test_evaluate_single_match(self):
        # Fact base: {p(a, b)}
        # Query atom: p(X, Y)
        # Expected: {X -> a, Y -> b}
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        atom = Atom(self.p, self.x, self.y)

        results = list(self.evaluator.evaluate(atom, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)
        self.assertEqual(results[0][self.y], self.b)

    def test_evaluate_multiple_matches(self):
        # Fact base: {p(a, b), p(a, c)}
        # Query atom: p(a, X)
        # Expected: {X -> b}, {X -> c}
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a, self.b),
            Atom(self.p, self.a, self.c),
        ])
        atom = Atom(self.p, self.a, self.x)

        results = list(self.evaluator.evaluate(atom, fact_base))

        self.assertEqual(len(results), 2)
        result_values = {r[self.x] for r in results}
        self.assertEqual(result_values, {self.b, self.c})

    def test_evaluate_no_match(self):
        # Fact base: {p(a, b)}
        # Query atom: q(X)
        # Expected: no matches
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        atom = Atom(self.q, self.x)

        results = list(self.evaluator.evaluate(atom, fact_base))

        self.assertEqual(len(results), 0)

    def test_evaluate_ground_atom_match(self):
        # Fact base: {p(a, b)}
        # Query atom: p(a, b)
        # Expected: empty substitution (match)
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        atom = Atom(self.p, self.a, self.b)

        results = list(self.evaluator.evaluate(atom, fact_base))

        self.assertEqual(len(results), 1)
        # Empty or identity substitution
        self.assertEqual(len(results[0]), 0)

    def test_evaluate_ground_atom_no_match(self):
        # Fact base: {p(a, b)}
        # Query atom: p(a, c)
        # Expected: no matches
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        atom = Atom(self.p, self.a, self.c)

        results = list(self.evaluator.evaluate(atom, fact_base))

        self.assertEqual(len(results), 0)

    def test_evaluate_with_initial_substitution(self):
        # Fact base: {p(a, b), p(a, c)}
        # Query atom: p(X, Y)
        # Initial sub: {X -> a}
        # Expected: {X -> a, Y -> b}, {X -> a, Y -> c}
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a, self.b),
            Atom(self.p, self.a, self.c),
        ])
        atom = Atom(self.p, self.x, self.y)
        initial_sub = Substitution({self.x: self.a})

        results = list(self.evaluator.evaluate(atom, fact_base, initial_sub))

        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r[self.x], self.a)

    def test_evaluate_empty_fact_base(self):
        # Fact base: {}
        # Query atom: p(X, Y)
        # Expected: no matches
        fact_base = MutableInMemoryFactBase()
        atom = Atom(self.p, self.x, self.y)

        results = list(self.evaluator.evaluate(atom, fact_base))

        self.assertEqual(len(results), 0)

    def test_evaluate_same_variable_twice(self):
        # Fact base: {p(a, a), p(a, b)}
        # Query atom: p(X, X)
        # Expected: {X -> a} (only p(a,a) matches)
        fact_base = MutableInMemoryFactBase([
            Atom(self.p, self.a, self.a),
            Atom(self.p, self.a, self.b),
        ])
        atom = Atom(self.p, self.x, self.x)

        results = list(self.evaluator.evaluate(atom, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)


if __name__ == "__main__":
    unittest.main()
