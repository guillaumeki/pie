"""
Tests for AtomEvaluator.
"""

import unittest
from unittest.mock import MagicMock, patch

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_config import LiteralConfig
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.data.collection.builder import (
    ReadableCollectionBuilder,
)
from prototyping_inference_engine.api.data.python_function_data import (
    PythonFunctionReadable,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.query_evaluation.evaluator.atom.atom_evaluator import (
    AtomEvaluator,
)
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
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.p, self.a, self.c),
            ]
        )
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
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.p, self.a, self.c),
            ]
        )
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
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.a),
                Atom(self.p, self.a, self.b),
            ]
        )
        atom = Atom(self.p, self.x, self.x)

        results = list(self.evaluator.evaluate(atom, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)

    def test_evaluate_with_python_function_term(self):
        def increment(term: Term) -> Term:
            identifier = term.identifier
            if isinstance(identifier, int):
                number = identifier
            else:
                number = int(str(identifier))
            return Constant(number + 1)

        pred = Predicate("p", 1)
        fact_base = MutableInMemoryFactBase([Atom(pred, Constant(2))])
        literal_factory = LiteralFactory(DictStorage(), LiteralConfig.default())
        functions = PythonFunctionReadable(literal_factory)
        functions.register_function("increment", increment, mode="terms")
        collection = (
            ReadableCollectionBuilder()
            .add_all_predicates_from(fact_base)
            .add_all_predicates_from(functions)
            .build()
        )

        atom = Atom(pred, EvaluableFunctionTerm("increment", [Constant(1)]))
        results = list(self.evaluator.evaluate(atom, collection))

        self.assertEqual(len(results), 1)

    def test_evaluate_uses_prepared_query(self):
        fact_base = MutableInMemoryFactBase([Atom(self.p, self.a, self.b)])
        atom = Atom(self.p, self.x, self.y)
        prepared = MagicMock()
        prepared.execute.return_value = iter([Substitution({self.x: self.a})])

        with patch(
            "prototyping_inference_engine.query_evaluation.evaluator.atom.atom_evaluator.prepare_atomic_or_conjunction"
        ) as mock_prepare:
            mock_prepare.return_value = prepared
            results = list(self.evaluator.evaluate(atom, fact_base))

        mock_prepare.assert_called_once()
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
