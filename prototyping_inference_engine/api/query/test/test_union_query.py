"""
Tests for UnionQuery.
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestUnionQueryBasics(unittest.TestCase):
    """Test basic UnionQuery functionality."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.a = Constant("a")
        self.b = Constant("b")

    def test_create_empty_union(self):
        """Test creating an empty UnionQuery."""
        uq = UnionQuery([], [self.x])
        self.assertEqual(len(uq), 0)
        self.assertEqual(uq.answer_variables, (self.x,))

    def test_create_single_query_union(self):
        """Test creating a UnionQuery with a single query."""
        cq = ConjunctiveQuery(
            FrozenAtomSet([Atom(self.p, self.x, self.y)]),
            [self.x],
        )
        uq = UnionQuery([cq], [self.x])

        self.assertEqual(len(uq), 1)
        self.assertEqual(uq.answer_variables, (self.x,))

    def test_create_multi_query_union(self):
        """Test creating a UnionQuery with multiple queries."""
        cq1 = ConjunctiveQuery(
            FrozenAtomSet([Atom(self.p, self.x, self.a)]),
            [self.x],
        )
        cq2 = ConjunctiveQuery(
            FrozenAtomSet([Atom(self.q, self.x)]),
            [self.x],
        )
        uq = UnionQuery([cq1, cq2], [self.x])

        self.assertEqual(len(uq), 2)

    def test_incompatible_answer_variables_raises(self):
        """Test that incompatible answer variable counts raise ValueError."""
        cq1 = ConjunctiveQuery(
            FrozenAtomSet([Atom(self.p, self.x, self.y)]),
            [self.x],
        )
        cq2 = ConjunctiveQuery(
            FrozenAtomSet([Atom(self.p, self.x, self.y)]),
            [self.x, self.y],  # Different count!
        )

        with self.assertRaises(ValueError):
            UnionQuery([cq1, cq2], [self.x])


class TestUnionQueryWithCQ(unittest.TestCase):
    """Test UnionQuery with ConjunctiveQuery."""

    def setUp(self):
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.a = Constant("a")
        self.b = Constant("b")

    def test_terms(self):
        """Test that terms() collects terms from all queries."""
        cq1 = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.a)]), [])
        cq2 = ConjunctiveQuery(FrozenAtomSet([Atom(self.q, self.b)]), [])
        uq = UnionQuery([cq1, cq2], [])

        self.assertIn(self.a, uq.terms)
        self.assertIn(self.b, uq.terms)

    def test_constants(self):
        """Test that constants() collects constants from all queries."""
        cq1 = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.a)]), [])
        cq2 = ConjunctiveQuery(FrozenAtomSet([Atom(self.q, self.b)]), [])
        uq = UnionQuery([cq1, cq2], [])

        self.assertEqual(uq.constants, {self.a, self.b})

    def test_variables(self):
        """Test that variables() collects variables from all queries."""
        y = Variable("Y")
        cq1 = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])
        cq2 = ConjunctiveQuery(FrozenAtomSet([Atom(self.q, y)]), [y])
        uq = UnionQuery([cq1, cq2], [self.x])

        # Y is renamed to X in cq2
        self.assertIn(self.x, uq.variables)


class TestUnionQueryWithFOQuery(unittest.TestCase):
    """Test UnionQuery with FOQuery."""

    def setUp(self):
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.a = Constant("a")

    def test_union_of_fo_queries(self):
        """Test creating a UnionQuery of FOQueries."""
        foq1 = FOQuery(Atom(self.p, self.x), [self.x])
        foq2 = FOQuery(Atom(self.q, self.x), [self.x])

        uq = UnionQuery([foq1, foq2], [self.x])

        self.assertEqual(len(uq), 2)
        self.assertEqual(uq.answer_variables, (self.x,))


class TestUnionQueryOperations(unittest.TestCase):
    """Test UnionQuery operations."""

    def setUp(self):
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.a = Constant("a")

    def test_or_operator(self):
        """Test the | operator for combining UnionQueries."""
        cq1 = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])
        cq2 = ConjunctiveQuery(FrozenAtomSet([Atom(self.q, self.x)]), [self.x])

        uq1 = UnionQuery([cq1], [self.x])
        uq2 = UnionQuery([cq2], [self.x])

        combined = uq1 | uq2

        self.assertEqual(len(combined), 2)

    def test_or_incompatible_raises(self):
        """Test that | raises for incompatible answer variables."""
        cq1 = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])
        cq2 = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.y)]), [self.y])

        uq1 = UnionQuery([cq1], [self.x])
        uq2 = UnionQuery([cq2], [self.y])

        with self.assertRaises(ValueError):
            _ = uq1 | uq2

    def test_apply_substitution(self):
        """Test applying a substitution to UnionQuery."""
        # Use a substitution that renames a variable to another variable
        z = Variable("Z")
        foq = FOQuery(Atom(self.p, self.x), [self.x])
        uq = UnionQuery([foq], [self.x])

        sub = Substitution({self.x: z})
        result = uq.apply_substitution(sub)

        # After substitution, X is renamed to Z
        self.assertIn(z, result.variables)
        self.assertEqual(result.answer_variables, (z,))

    def test_iteration(self):
        """Test iterating over queries in UnionQuery."""
        cq1 = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])
        cq2 = ConjunctiveQuery(FrozenAtomSet([Atom(self.q, self.x)]), [self.x])
        uq = UnionQuery([cq1, cq2], [self.x])

        queries = list(uq)
        self.assertEqual(len(queries), 2)

    def test_equality(self):
        """Test UnionQuery equality."""
        cq = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])

        uq1 = UnionQuery([cq], [self.x])
        uq2 = UnionQuery([cq], [self.x])

        self.assertEqual(uq1, uq2)

    def test_hash(self):
        """Test that equal UnionQueries have the same hash."""
        cq = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])

        uq1 = UnionQuery([cq], [self.x])
        uq2 = UnionQuery([cq], [self.x])

        self.assertEqual(hash(uq1), hash(uq2))

    def test_str_representation(self):
        """Test string representation."""
        cq = ConjunctiveQuery(FrozenAtomSet([Atom(self.p, self.x)]), [self.x])
        uq = UnionQuery([cq], [self.x])

        s = str(uq)
        self.assertIn("X", s)


if __name__ == "__main__":
    unittest.main()
