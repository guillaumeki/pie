"""
Tests for FOQuery and FOQueryFactory.
"""
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.api.formula import (
    ConjunctionFormula,
    DisjunctionFormula,
    NegationFormula,
    ExistentialFormula,
    UniversalFormula,
)
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestFOQuery(unittest.TestCase):
    """Test FOQuery class."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.z = Variable("Z")
        self.a = Constant("a")

    def test_create_simple_query(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x])
        self.assertEqual(query.formula, atom)
        self.assertEqual(query.answer_variables, (self.x,))

    def test_create_boolean_query(self):
        atom = Atom(self.p, self.a, self.a)
        query = FOQuery(atom)
        self.assertTrue(query.is_boolean)
        self.assertEqual(len(query.answer_variables), 0)

    def test_create_query_with_label(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x], label="my_query")
        self.assertEqual(query.label, "my_query")

    def test_invalid_answer_variable_raises(self):
        atom = Atom(self.p, self.x, self.y)
        with self.assertRaises(ValueError):
            FOQuery(atom, [self.z])  # Z is not in the formula

    def test_formula_property(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x])
        self.assertIsInstance(query.formula, Atom)

    def test_free_variables(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x])
        self.assertEqual(query.free_variables, frozenset([self.x, self.y]))

    def test_bound_variables(self):
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.y, atom)
        query = FOQuery(exists, [self.x])
        self.assertEqual(query.bound_variables, frozenset([self.y]))

    def test_existential_variables(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x])
        self.assertEqual(query.existential_variables, {self.y})

    def test_atoms(self):
        p_xy = Atom(self.p, self.x, self.y)
        q_y = Atom(self.q, self.y)
        conj = ConjunctionFormula(p_xy, q_y)
        query = FOQuery(conj, [self.x])
        self.assertEqual(query.atoms, frozenset([p_xy, q_y]))

    def test_terms(self):
        atom = Atom(self.p, self.x, self.a)
        query = FOQuery(atom, [self.x])
        self.assertEqual(query.terms, {self.x, self.a})

    def test_variables(self):
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.y, atom)
        query = FOQuery(exists, [self.x])
        self.assertEqual(query.variables, {self.x, self.y})

    def test_constants(self):
        b = Constant("b")
        atom = Atom(self.p, self.x, self.a)
        query = FOQuery(atom, [self.x])
        self.assertIn(self.a, query.constants)

    def test_is_closed_false(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x])
        self.assertFalse(query.is_closed)

    def test_is_closed_true(self):
        atom = Atom(self.p, self.a, self.a)
        query = FOQuery(atom)
        self.assertTrue(query.is_closed)

    def test_str_representation(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x])
        self.assertIn("?(X)", str(query))
        self.assertIn("p(X, Y)", str(query))

    def test_str_without_answer_variables(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x])
        self.assertEqual(query.str_without_answer_variables, "p(X, Y)")

    def test_apply_substitution(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x])
        sub = Substitution({self.y: self.z})
        result = query.apply_substitution(sub)
        self.assertIsInstance(result, FOQuery)
        self.assertEqual(result.formula, Atom(self.p, self.x, self.z))

    def test_apply_substitution_to_answer_var(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x, self.y])
        sub = Substitution({self.x: self.z})
        result = query.apply_substitution(sub)
        self.assertIn(self.z, result.answer_variables)

    def test_equality(self):
        atom = Atom(self.p, self.x, self.y)
        q1 = FOQuery(atom, [self.x])
        q2 = FOQuery(atom, [self.x])
        self.assertEqual(q1, q2)

    def test_inequality_different_formula(self):
        atom1 = Atom(self.p, self.x, self.y)
        atom2 = Atom(self.q, self.x)
        q1 = FOQuery(atom1, [self.x])
        q2 = FOQuery(atom2, [self.x])
        self.assertNotEqual(q1, q2)

    def test_inequality_different_answer_vars(self):
        atom = Atom(self.p, self.x, self.y)
        q1 = FOQuery(atom, [self.x])
        q2 = FOQuery(atom, [self.y])
        self.assertNotEqual(q1, q2)

    def test_hash(self):
        atom = Atom(self.p, self.x, self.y)
        q1 = FOQuery(atom, [self.x])
        q2 = FOQuery(atom, [self.x])
        self.assertEqual(hash(q1), hash(q2))

    def test_answer_atom(self):
        atom = Atom(self.p, self.x, self.y)
        query = FOQuery(atom, [self.x, self.y])
        ans_atom = query.answer_atom
        self.assertEqual(ans_atom.predicate.name, "ans")
        self.assertEqual(ans_atom.predicate.arity, 2)


class TestFOQueryWithQuantifiers(unittest.TestCase):
    """Test FOQuery with quantified formulas."""

    def setUp(self):
        self.p = Predicate("p", 2)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")

    def test_existential_query(self):
        # ?(X) :- ∃Y.p(X,Y)
        atom = Atom(self.p, self.x, self.y)
        exists = ExistentialFormula(self.y, atom)
        query = FOQuery(exists, [self.x])

        self.assertEqual(query.free_variables, frozenset([self.x]))
        self.assertEqual(query.bound_variables, frozenset([self.y]))
        self.assertIn("∃Y", str(query))

    def test_universal_query(self):
        # ?() :- ∀X.p(X,a)
        a = Constant("a")
        atom = Atom(self.p, self.x, a)
        forall = UniversalFormula(self.x, atom)
        query = FOQuery(forall)

        self.assertTrue(query.is_boolean)
        self.assertTrue(query.is_closed)

    def test_nested_quantifiers(self):
        # ?(X) :- ∃Y.∃Z.(p(X,Y) ∧ p(Y,Z))
        z = Variable("Z")
        p_xy = Atom(self.p, self.x, self.y)
        p_yz = Atom(self.p, self.y, z)
        conj = ConjunctionFormula(p_xy, p_yz)
        exists_z = ExistentialFormula(z, conj)
        exists_y = ExistentialFormula(self.y, exists_z)
        query = FOQuery(exists_y, [self.x])

        self.assertEqual(query.free_variables, frozenset([self.x]))
        self.assertEqual(query.bound_variables, frozenset([self.y, z]))


class TestFOQueryFactory(unittest.TestCase):
    """Test FOQueryFactory."""

    def setUp(self):
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()

    def test_from_formula_with_string_vars(self):
        formula = self.session.formula().atom("p", "X", "Y").build()
        query = self.session.fo_query().from_formula(formula, ["X"])
        self.assertEqual(len(query.answer_variables), 1)

    def test_from_formula_with_variable_objects(self):
        formula = self.session.formula().atom("p", "X", "Y").build()
        x = self.session.variable("X")
        query = self.session.fo_query().from_formula(formula, [x])
        self.assertEqual(query.answer_variables[0], x)

    def test_from_formula_with_label(self):
        formula = self.session.formula().atom("p", "X").build()
        query = self.session.fo_query().from_formula(formula, ["X"], label="test")
        self.assertEqual(query.label, "test")

    def test_builder_returns_builder(self):
        from prototyping_inference_engine.api.query.fo_query_factory import FOQueryBuilder
        builder = self.session.fo_query().builder()
        self.assertIsInstance(builder, FOQueryBuilder)


class TestFOQueryBuilder(unittest.TestCase):
    """Test FOQueryBuilder fluent API."""

    def setUp(self):
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()

    def test_build_simple_query(self):
        query = (self.session.fo_query().builder()
            .answer("X")
            .atom("p", "X", "Y")
            .build())
        self.assertIsInstance(query, FOQuery)
        self.assertEqual(len(query.answer_variables), 1)

    def test_build_query_multiple_answers(self):
        query = (self.session.fo_query().builder()
            .answer("X", "Y")
            .atom("p", "X", "Y")
            .build())
        self.assertEqual(len(query.answer_variables), 2)

    def test_build_query_with_label(self):
        query = (self.session.fo_query().builder()
            .label("my_query")
            .answer("X")
            .atom("p", "X")
            .build())
        self.assertEqual(query.label, "my_query")

    def test_build_query_with_conjunction(self):
        query = (self.session.fo_query().builder()
            .answer("X")
            .atom("p", "X", "Y")
            .and_()
            .atom("q", "Y")
            .build())
        self.assertIsInstance(query.formula, ConjunctionFormula)

    def test_build_query_with_disjunction(self):
        query = (self.session.fo_query().builder()
            .answer("X")
            .atom("p", "X")
            .or_()
            .atom("q", "X")
            .build())
        self.assertIsInstance(query.formula, DisjunctionFormula)

    def test_build_query_with_negation(self):
        query = (self.session.fo_query().builder()
            .answer("X")
            .atom("p", "X")
            .not_()
            .build())
        self.assertIsInstance(query.formula, NegationFormula)

    def test_build_query_with_existential(self):
        query = (self.session.fo_query().builder()
            .answer("X")
            .exists("Y")
            .atom("p", "X", "Y")
            .build())
        self.assertIsInstance(query.formula, ExistentialFormula)
        self.assertEqual(query.free_variables, frozenset([self.session.variable("X")]))

    def test_build_query_with_universal(self):
        query = (self.session.fo_query().builder()
            .forall("X")
            .atom("p", "X")
            .build())
        self.assertIsInstance(query.formula, UniversalFormula)
        self.assertTrue(query.is_boolean)

    def test_build_complex_query(self):
        # ?(X) :- ∃Y.(p(X,Y) ∧ q(Y))
        query = (self.session.fo_query().builder()
            .answer("X")
            .exists("Y")
            .atom("p", "X", "Y")
            .and_()
            .atom("q", "Y")
            .build())

        self.assertIsInstance(query.formula, ExistentialFormula)
        self.assertIsInstance(query.formula.inner, ConjunctionFormula)
        x = self.session.variable("X")
        y = self.session.variable("Y")
        self.assertEqual(query.free_variables, frozenset([x]))
        self.assertEqual(query.bound_variables, frozenset([y]))

    def test_build_without_formula_raises(self):
        builder = self.session.fo_query().builder().answer("X")
        with self.assertRaises(ValueError):
            builder.build()

    def test_builder_chaining(self):
        builder = self.session.fo_query().builder()
        result = builder.answer("X").atom("p", "X")
        self.assertIs(result, builder)


class TestFOQueryFromSession(unittest.TestCase):
    """Test FOQuery creation via ReasoningSession."""

    def test_fo_query_method_exists(self):
        with ReasoningSession.create() as session:
            factory = session.fo_query()
            self.assertIsNotNone(factory)

    def test_session_closed_raises_error(self):
        session = ReasoningSession.create()
        session.close()
        with self.assertRaises(RuntimeError):
            session.fo_query()

    def test_full_workflow(self):
        with ReasoningSession.create() as session:
            # Build query: ?(X) :- ∃Y.(p(X,Y) ∧ ¬q(Y))
            query = (session.fo_query().builder()
                .answer("X")
                .exists("Y")
                .atom("p", "X", "Y")
                .and_()
                .atom("q", "Y")
                .not_()
                .build())

            self.assertIsInstance(query, FOQuery)
            self.assertEqual(len(query.answer_variables), 1)
            self.assertIn("?(X)", str(query))


if __name__ == "__main__":
    unittest.main()
