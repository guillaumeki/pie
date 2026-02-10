"""
Tests for conjunction evaluation via FOQuery evaluators.
"""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate, SpecialPredicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


def _evaluate_formula(evaluator, formula, data, substitution=None):
    query = FOQuery(formula, sorted(formula.free_variables, key=lambda v: str(v)))
    return list(evaluator.evaluate(query, data, substitution))


class TestConjunctionEvaluation(unittest.TestCase):
    """Test conjunction evaluation via FOQuery evaluators."""

    @classmethod
    def setUpClass(cls):
        # Predicates
        cls.p = Predicate("p", 2)
        cls.q = Predicate("q", 1)
        cls.r = Predicate("r", 2)

        # Variables
        cls.x = Variable("X")
        cls.y = Variable("Y")
        cls.z = Variable("Z")

        # Constants
        cls.a = Constant("a")
        cls.b = Constant("b")
        cls.c = Constant("c")
        cls.d = Constant("d")

    def setUp(self):
        self.evaluator = GenericFOQueryEvaluator()

    def test_simple_conjunction_single_match(self):
        """
        Query: p(X,Y) ∧ q(Y)
        FactBase: {p(a,b), q(b)}
        Expected: {X→a, Y→b}
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.q, self.b),
            ]
        )
        formula = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(self.q, self.y),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)
        self.assertEqual(results[0][self.y], self.b)

    def test_simple_conjunction_multiple_matches(self):
        """
        Query: p(X,Y) ∧ q(Y)
        FactBase: {p(a,b), p(c,b), q(b)}
        Expected: {X→a, Y→b}, {X→c, Y→b}
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.p, self.c, self.b),
                Atom(self.q, self.b),
            ]
        )
        formula = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(self.q, self.y),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 2)
        x_values = {r[self.x] for r in results}
        self.assertEqual(x_values, {self.a, self.c})

    def test_conjunction_no_match(self):
        """
        Query: p(X,Y) ∧ q(Y)
        FactBase: {p(a,b), q(c)}  (no q(b))
        Expected: empty
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.q, self.c),
            ]
        )
        formula = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(self.q, self.y),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 0)

    def test_conjunction_with_initial_substitution(self):
        """
        Query: p(X,Y) ∧ q(Y) with {X→a}
        FactBase: {p(a,b), p(c,b), q(b)}
        Expected: {X→a, Y→b}
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.p, self.c, self.b),
                Atom(self.q, self.b),
            ]
        )
        formula = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(self.q, self.y),
        )
        initial_sub = Substitution({self.x: self.a})

        results = _evaluate_formula(self.evaluator, formula, fact_base, initial_sub)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)
        self.assertEqual(results[0][self.y], self.b)

    def test_nested_conjunction_left(self):
        """
        Query: (p(X,Y) ∧ q(Y)) ∧ r(Y,Z)
        FactBase: {p(a,b), q(b), r(b,c)}
        Expected: {X→a, Y→b, Z→c}
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.q, self.b),
                Atom(self.r, self.b, self.c),
            ]
        )
        inner = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(self.q, self.y),
        )
        formula = ConjunctionFormula(inner, Atom(self.r, self.y, self.z))

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)
        self.assertEqual(results[0][self.y], self.b)
        self.assertEqual(results[0][self.z], self.c)

    def test_nested_conjunction_right(self):
        """
        Query: p(X,Y) ∧ (q(Y) ∧ r(Y,Z))
        FactBase: {p(a,b), q(b), r(b,c)}
        Expected: {X→a, Y→b, Z→c}
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.q, self.b),
                Atom(self.r, self.b, self.c),
            ]
        )
        inner = ConjunctionFormula(
            Atom(self.q, self.y),
            Atom(self.r, self.y, self.z),
        )
        formula = ConjunctionFormula(Atom(self.p, self.x, self.y), inner)

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)
        self.assertEqual(results[0][self.y], self.b)
        self.assertEqual(results[0][self.z], self.c)

    def test_deeply_nested_conjunction(self):
        """
        Query: ((p(X,Y) ∧ q(Y)) ∧ r(Y,Z)) ∧ p(Z,W)
        FactBase: {p(a,b), q(b), r(b,c), p(c,d)}
        Expected: {X→a, Y→b, Z→c, W→d}
        """
        w = Variable("W")
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.q, self.b),
                Atom(self.r, self.b, self.c),
                Atom(self.p, self.c, self.d),
            ]
        )
        inner1 = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(self.q, self.y),
        )
        inner2 = ConjunctionFormula(inner1, Atom(self.r, self.y, self.z))
        formula = ConjunctionFormula(inner2, Atom(self.p, self.z, w))

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)
        self.assertEqual(results[0][self.y], self.b)
        self.assertEqual(results[0][self.z], self.c)
        self.assertEqual(results[0][w], self.d)

    def test_conjunction_cartesian_product(self):
        """
        Query: p(X) ∧ q(Y) (no shared variables)
        FactBase: {p(a), p(b), q(c), q(d)}
        Expected: 4 results (cartesian product)
        """
        p1 = Predicate("p", 1)
        q1 = Predicate("q", 1)
        fact_base = MutableInMemoryFactBase(
            [
                Atom(p1, self.a),
                Atom(p1, self.b),
                Atom(q1, self.c),
                Atom(q1, self.d),
            ]
        )
        formula = ConjunctionFormula(
            Atom(p1, self.x),
            Atom(q1, self.y),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 4)

    def test_conjunction_same_variable(self):
        """
        Query: p(X,Y) ∧ q(X,Z)
        FactBase: {p(a,b), p(c,d), q(a,e), q(c,f)}
        Expected: {X→a, Y→b, Z→e}, {X→c, Y→d, Z→f}
        """
        e = Constant("e")
        f = Constant("f")
        q2 = Predicate("q", 2)
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.p, self.c, self.d),
                Atom(q2, self.a, e),
                Atom(q2, self.c, f),
            ]
        )
        formula = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(q2, self.x, self.z),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 2)
        result_pairs = {(r[self.x], r[self.z]) for r in results}
        self.assertEqual(result_pairs, {(self.a, e), (self.c, f)})


class TestConjunctionWithEquality(unittest.TestCase):
    """Test conjunction evaluation with equality atoms."""

    @classmethod
    def setUpClass(cls):
        cls.p = Predicate("p", 2)
        cls.q = Predicate("q", 1)
        cls.eq = SpecialPredicate.EQUALITY.value
        cls.x = Variable("X")
        cls.y = Variable("Y")
        cls.z = Variable("Z")
        cls.a = Constant("a")
        cls.b = Constant("b")
        cls.c = Constant("c")

    def setUp(self):
        self.evaluator = GenericFOQueryEvaluator()

    def test_equality_variable_constant(self):
        """
        Query: p(X,Y) ∧ X=a
        FactBase: {p(a,b), p(c,d)}
        Expected: {X→a, Y→b}
        """
        d = Constant("d")
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.p, self.c, d),
            ]
        )
        formula = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(self.eq, self.x, self.a),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)
        self.assertEqual(results[0][self.y], self.b)

    def test_equality_two_variables(self):
        """
        Query: p(X,Y) ∧ q(Z) ∧ Y=Z
        FactBase: {p(a,b), q(b)}
        Expected: {X→a, Y→b, Z→b}
        """
        fact_base = MutableInMemoryFactBase(
            [
                Atom(self.p, self.a, self.b),
                Atom(self.q, self.b),
            ]
        )
        conj1 = ConjunctionFormula(
            Atom(self.p, self.x, self.y),
            Atom(self.q, self.z),
        )
        formula = ConjunctionFormula(
            conj1,
            Atom(self.eq, self.y, self.z),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.a)
        # Y and Z should both be b (or one maps to the other)
        self.assertEqual(results[0].apply(self.y), self.b)
        self.assertEqual(results[0].apply(self.z), self.b)

    def test_equality_transitive(self):
        """
        Query: p(X) ∧ q(Y) ∧ r(Z) ∧ X=Y ∧ Y=Z
        FactBase: {p(a), q(a), r(a)}
        Expected: {X→a, Y→a, Z→a}
        """
        p1 = Predicate("p", 1)
        q1 = Predicate("q", 1)
        r1 = Predicate("r", 1)
        fact_base = MutableInMemoryFactBase(
            [
                Atom(p1, self.a),
                Atom(q1, self.a),
                Atom(r1, self.a),
            ]
        )
        conj1 = ConjunctionFormula(Atom(p1, self.x), Atom(q1, self.y))
        conj2 = ConjunctionFormula(conj1, Atom(r1, self.z))
        conj3 = ConjunctionFormula(conj2, Atom(self.eq, self.x, self.y))
        formula = ConjunctionFormula(conj3, Atom(self.eq, self.y, self.z))

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        # All three should map to 'a'
        self.assertEqual(results[0].apply(self.x), self.a)
        self.assertEqual(results[0].apply(self.y), self.a)
        self.assertEqual(results[0].apply(self.z), self.a)

    def test_equality_inconsistent_constants(self):
        """
        Query: p(X) ∧ X=a ∧ X=b (where a≠b)
        Expected: no results (inconsistent)
        """
        p1 = Predicate("p", 1)
        fact_base = MutableInMemoryFactBase(
            [
                Atom(p1, self.a),
                Atom(p1, self.b),
            ]
        )
        conj1 = ConjunctionFormula(
            Atom(p1, self.x),
            Atom(self.eq, self.x, self.a),
        )
        formula = ConjunctionFormula(
            conj1,
            Atom(self.eq, self.x, self.b),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 0)

    def test_equality_same_constant(self):
        """
        Query: p(X) ∧ a=a
        FactBase: {p(b)}
        Expected: {X→b}
        """
        p1 = Predicate("p", 1)
        fact_base = MutableInMemoryFactBase(
            [
                Atom(p1, self.b),
            ]
        )
        formula = ConjunctionFormula(
            Atom(p1, self.x),
            Atom(self.eq, self.a, self.a),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.x], self.b)

    def test_equality_only(self):
        """
        Query: X=a ∧ Y=X (only equalities, no regular atoms)
        FactBase: empty
        Expected: {X→a, Y→a}
        """
        fact_base = MutableInMemoryFactBase([])
        formula = ConjunctionFormula(
            Atom(self.eq, self.x, self.a),
            Atom(self.eq, self.y, self.x),
        )

        results = _evaluate_formula(self.evaluator, formula, fact_base)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].apply(self.x), self.a)
        self.assertEqual(results[0].apply(self.y), self.a)


class TestConjunctionFOQuery(unittest.TestCase):
    """Test FOQuery with conjunction formulas."""

    def setUp(self):
        self.evaluator = GenericFOQueryEvaluator()

    def test_conjunction_query_with_answer_vars(self):
        """
        Query: ?(X) :- ∃Y.(p(X,Y) ∧ q(Y))
        FactBase: {p(a,b), p(c,b), q(b)}
        Expected: {a}, {c}
        """
        p = Predicate("p", 2)
        q = Predicate("q", 1)
        x = Variable("X")
        y = Variable("Y")
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        fact_base = MutableInMemoryFactBase(
            [
                Atom(p, a, b),
                Atom(p, c, b),
                Atom(q, b),
            ]
        )
        conj = ConjunctionFormula(Atom(p, x, y), Atom(q, y))
        formula = ExistentialFormula(y, conj)
        query = FOQuery(formula, [x])

        results = list(self.evaluator.evaluate_and_project(query, fact_base))

        self.assertEqual(len(results), 2)
        result_values = {r[0] for r in results}
        self.assertEqual(result_values, {a, c})

    def test_boolean_conjunction_query_true(self):
        """
        Query: ?() :- p(a,b) ∧ q(b)
        FactBase: {p(a,b), q(b)}
        Expected: true (one empty tuple)
        """
        p = Predicate("p", 2)
        q = Predicate("q", 1)
        a = Constant("a")
        b = Constant("b")

        fact_base = MutableInMemoryFactBase(
            [
                Atom(p, a, b),
                Atom(q, b),
            ]
        )
        formula = ConjunctionFormula(Atom(p, a, b), Atom(q, b))
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate_and_project(query, fact_base))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ())

    def test_boolean_conjunction_query_false(self):
        """
        Query: ?() :- p(a,b) ∧ q(c)
        FactBase: {p(a,b), q(b)}  (no q(c))
        Expected: false (empty)
        """
        p = Predicate("p", 2)
        q = Predicate("q", 1)
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")

        fact_base = MutableInMemoryFactBase(
            [
                Atom(p, a, b),
                Atom(q, b),
            ]
        )
        formula = ConjunctionFormula(Atom(p, a, b), Atom(q, c))
        query = FOQuery(formula, [])

        results = list(self.evaluator.evaluate_and_project(query, fact_base))

        self.assertEqual(len(results), 0)


class TestConjunctionWithSession(unittest.TestCase):
    """Test conjunction evaluation via ReasoningSession."""

    def setUp(self):
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()

    def test_conjunction_query_via_builder(self):
        """Test building and evaluating a conjunction query."""
        result = self.session.parse("""
            parent(alice, bob).
            parent(alice, carol).
            parent(bob, dave).
            male(bob).
            male(dave).
        """)
        fb = self.session.create_fact_base(result.facts)

        # Query: Who are Alice's male children?
        # ?(X) :- parent(alice, X) ∧ male(X)
        query = (
            self.session.fo_query()
            .builder()
            .answer("X")
            .atom("parent", "alice", "X")
            .and_()
            .atom("male", "X")
            .build()
        )

        results = list(self.session.evaluate_query(query, fb))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].identifier, "bob")

    def test_three_way_conjunction(self):
        """Test a three-way conjunction."""
        result = self.session.parse("""
            edge(a, b).
            edge(b, c).
            edge(c, d).
        """)
        fb = self.session.create_fact_base(result.facts)

        # Query: paths of length 3
        # ?(X,Y,Z,W) :- edge(X,Y) ∧ edge(Y,Z) ∧ edge(Z,W)
        query = (
            self.session.fo_query()
            .builder()
            .answer("X", "Y", "Z", "W")
            .atom("edge", "X", "Y")
            .and_()
            .atom("edge", "Y", "Z")
            .and_()
            .atom("edge", "Z", "W")
            .build()
        )

        results = list(self.session.evaluate_query(query, fb))

        self.assertEqual(len(results), 1)
        path = tuple(t.identifier for t in results[0])
        self.assertEqual(path, ("a", "b", "c", "d"))

    def test_conjunction_with_no_shared_variables(self):
        """Test conjunction where sub-formulas have no shared variables."""
        result = self.session.parse("""
            p(a).
            p(b).
            q(c).
        """)
        fb = self.session.create_fact_base(result.facts)

        # ?(X,Y) :- p(X) ∧ q(Y)
        query = (
            self.session.fo_query()
            .builder()
            .answer("X", "Y")
            .atom("p", "X")
            .and_()
            .atom("q", "Y")
            .build()
        )

        results = list(self.session.evaluate_query(query, fb))

        # Cartesian product: 2 * 1 = 2 results
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
