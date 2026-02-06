from unittest import TestCase

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import (
    UnionConjunctiveQueries,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.io.parsers.dlgp.dlgp2_parser import Dlgp2Parser


class TestConjunctiveQuery(TestCase):
    def test_creation_empty(self):
        """Test creating empty ConjunctiveQuery."""
        cq = ConjunctiveQuery()
        self.assertEqual(len(cq.atoms), 0)
        self.assertEqual(cq.answer_variables, ())

    def test_creation_with_atoms(self):
        """Test creating ConjunctiveQuery with atoms."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        self.assertEqual(len(cq.atoms), 2)
        self.assertEqual(cq.answer_variables, (x,))

    def test_variables_property(self):
        """Test variables property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        self.assertEqual(cq.variables, {Variable("X"), Variable("Y"), Variable("Z")})

    def test_constants_property(self):
        """Test constants property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,a), q(b,Y).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        self.assertEqual(cq.constants, {Constant("a"), Constant("b")})

    def test_terms_property(self):
        """Test terms property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,a).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        terms = cq.terms
        self.assertIn(Variable("X"), terms)
        self.assertIn(Constant("a"), terms)

    def test_existential_variables(self):
        """Test existential_variables property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        existential = cq.existential_variables
        self.assertEqual(existential, {Variable("Y"), Variable("Z")})

    def test_answer_atom(self):
        """Test answer_atom property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        ans_atom = cq.answer_atom
        self.assertEqual(ans_atom.predicate.name, "ans")
        self.assertEqual(ans_atom.predicate.arity, 1)
        self.assertEqual(ans_atom.terms, (x,))

    def test_apply_substitution(self):
        """Test applying substitution to ConjunctiveQuery."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        y = Variable("Y")
        cq = ConjunctiveQuery(atoms, [x])
        sub = Substitution({x: Variable("Z"), y: Constant("a")})
        result = cq.apply_substitution(sub)
        self.assertEqual(result.answer_variables, (Variable("Z"),))
        self.assertIn(Constant("a"), result.constants)

    def test_aggregate(self):
        """Test aggregating two ConjunctiveQueries."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        aggregated = cq1.aggregate(cq2)
        self.assertEqual(len(aggregated.atoms), 2)
        self.assertEqual(aggregated.answer_variables, (x, y))

    def test_equality_same_queries(self):
        """Test equality of identical queries."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms, [x])
        cq2 = ConjunctiveQuery(atoms, [x])
        self.assertEqual(cq1, cq2)

    def test_equality_different_atoms(self):
        """Test inequality of queries with different atoms."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(X).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        self.assertNotEqual(cq1, cq2)

    def test_hash(self):
        """Test that ConjunctiveQuery is hashable."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        h = hash(cq)
        self.assertIsInstance(h, int)

    def test_str(self):
        """Test string representation."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        s = str(cq)
        self.assertIn("X", s)
        self.assertIn("p", s)

    def test_repr(self):
        """Test repr representation."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        r = repr(cq)
        self.assertTrue(r.startswith("ConjunctiveQuery:"))

    def test_answer_variable_must_appear_in_atoms(self):
        """Test that answer variables must appear in atoms."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        y = Variable("Y")  # Y does not appear in atoms
        with self.assertRaises(ValueError):
            ConjunctiveQuery(atoms, [y])

    def test_query_with_other_answer_variables(self):
        """Test creating query with different answer variables."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms, [x])
        cq2 = cq1.query_with_other_answer_variables((y,))
        self.assertEqual(cq2.answer_variables, (y,))

    def test_pre_substitution(self):
        """Test ConjunctiveQuery with pre_substitution."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        a = Constant("a")
        pre_sub = Substitution({x: a})
        cq = ConjunctiveQuery(atoms, [x], pre_substitution=pre_sub)
        self.assertEqual(cq.pre_substitution[x], a)

    def test_pre_substitution_must_be_on_answer_variables(self):
        """Test that pre_substitution can only be on answer variables."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        y = Variable("Y")
        pre_sub = Substitution({y: Constant("a")})  # Y is not answer variable
        with self.assertRaises(ValueError):
            ConjunctiveQuery(atoms, [x], pre_substitution=pre_sub)


class TestUnionConjunctiveQueries(TestCase):
    def test_creation_empty(self):
        """Test creating empty UCQ."""
        ucq = UnionConjunctiveQueries()
        self.assertEqual(len(ucq), 0)

    def test_creation_with_cqs(self):
        """Test creating UCQ with conjunctive queries."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq = UnionConjunctiveQueries([cq1, cq2], [Variable("Z")])
        self.assertEqual(len(ucq), 2)

    def test_conjunctive_queries_property(self):
        """Test conjunctive_queries property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        ucq = UnionConjunctiveQueries([cq], [Variable("Z")])
        self.assertIsInstance(ucq.conjunctive_queries, frozenset)
        self.assertEqual(len(ucq.conjunctive_queries), 1)

    def test_variables_property(self):
        """Test variables property."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Z).")
        x = Variable("X")
        z = Variable("Z")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [z])
        ucq = UnionConjunctiveQueries([cq1, cq2], [Variable("W")])
        # Variables include answer variable W and all body variables
        self.assertIn(Variable("W"), ucq.variables)

    def test_constants_property(self):
        """Test constants property."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,a).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y,b).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq = UnionConjunctiveQueries([cq1, cq2], [Variable("Z")])
        self.assertEqual(ucq.constants, {Constant("a"), Constant("b")})

    def test_terms_property(self):
        """Test terms property."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,a).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        ucq = UnionConjunctiveQueries([cq], [Variable("Z")])
        terms = ucq.terms
        self.assertIn(Constant("a"), terms)

    def test_apply_substitution(self):
        """Test applying substitution to UCQ."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        z = Variable("Z")
        ucq = UnionConjunctiveQueries([cq], [z])
        sub = Substitution({z: Variable("W")})
        result = ucq.apply_substitution(sub)
        self.assertEqual(result.answer_variables, (Variable("W"),))

    def test_union_operator(self):
        """Test | operator for union."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq1 = UnionConjunctiveQueries([cq1], [z])
        ucq2 = UnionConjunctiveQueries([cq2], [z])
        combined = ucq1 | ucq2
        self.assertEqual(len(combined), 2)

    def test_union_different_answer_variables_raises(self):
        """Test that union with different answer variables raises."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq1 = UnionConjunctiveQueries([cq1], [Variable("Z")])
        ucq2 = UnionConjunctiveQueries([cq2], [Variable("W")])
        with self.assertRaises(ValueError):
            ucq1 | ucq2

    def test_equality(self):
        """Test equality of UCQs."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        z = Variable("Z")
        ucq1 = UnionConjunctiveQueries([cq], [z])
        ucq2 = UnionConjunctiveQueries([cq], [z])
        self.assertEqual(ucq1, ucq2)

    def test_hash(self):
        """Test that UCQ is hashable."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        ucq = UnionConjunctiveQueries([cq], [Variable("Z")])
        h = hash(ucq)
        self.assertIsInstance(h, int)

    def test_iter(self):
        """Test iteration over UCQ."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq = UnionConjunctiveQueries([cq1, cq2], [Variable("Z")])
        cqs = list(ucq)
        self.assertEqual(len(cqs), 2)

    def test_len(self):
        """Test __len__ method."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq = UnionConjunctiveQueries([cq1, cq2], [Variable("Z")])
        self.assertEqual(len(ucq), 2)

    def test_str(self):
        """Test string representation."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        ucq = UnionConjunctiveQueries([cq], [Variable("Z")])
        s = str(ucq)
        self.assertIn("Z", s)

    def test_repr(self):
        """Test repr representation."""
        ucq = UnionConjunctiveQueries()
        r = repr(ucq)
        self.assertTrue(r.startswith("UCQ:"))

    def test_mismatched_answer_variable_count_raises(self):
        """Test that CQs with wrong number of answer variables raises."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        y = Variable("Y")
        cq = ConjunctiveQuery(atoms1, [x, y])  # 2 answer variables
        with self.assertRaises(ValueError):
            UnionConjunctiveQueries([cq], [Variable("Z")])  # Only 1 expected


class TestCQToFOQueryConversion(TestCase):
    """Test conversion from CQ/UCQ to FOQuery."""

    def test_cq_to_fo_query_simple(self):
        """Test converting a simple CQ to FOQuery."""
        from prototyping_inference_engine.api.query.fo_query import FOQuery

        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        y = Variable("Y")
        cq = ConjunctiveQuery(atoms, [x, y])

        fo_query = cq.to_fo_query()

        self.assertIsInstance(fo_query, FOQuery)
        self.assertEqual(set(fo_query.answer_variables), {x, y})
        # Formula should be just the atom (no existential quantifiers)
        self.assertEqual(fo_query.formula.atoms, cq.atoms)

    def test_cq_to_fo_query_with_existential(self):
        """Test converting a CQ with existentially quantified variable."""
        from prototyping_inference_engine.api.formula.existential_formula import (
            ExistentialFormula,
        )
        from prototyping_inference_engine.api.query.fo_query import FOQuery

        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])  # Y and Z are existential

        fo_query = cq.to_fo_query()

        self.assertIsInstance(fo_query, FOQuery)
        self.assertEqual(fo_query.answer_variables, (x,))
        # Formula should be wrapped in existential quantifiers for Y and Z
        self.assertIsInstance(fo_query.formula, ExistentialFormula)
        self.assertEqual(fo_query.free_variables, frozenset({x}))

    def test_cq_existential_variables(self):
        """Test existential_variables property on CQ."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")
        cq = ConjunctiveQuery(atoms, [x])

        self.assertEqual(cq.existential_variables, frozenset({y, z}))

    def test_ucq_to_fo_query_single_cq(self):
        """Test converting a UCQ with one CQ to FOQuery."""
        from prototyping_inference_engine.api.query.fo_query import FOQuery

        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        ucq = UnionConjunctiveQueries([cq], [x])

        fo_query = ucq.to_fo_query()

        self.assertIsInstance(fo_query, FOQuery)
        self.assertEqual(fo_query.answer_variables, (x,))

    def test_ucq_to_fo_query_multiple_cqs(self):
        """Test converting a UCQ with multiple CQs to FOQuery."""
        from prototyping_inference_engine.api.formula.disjunction_formula import (
            DisjunctionFormula,
        )
        from prototyping_inference_engine.api.query.fo_query import FOQuery

        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq = UnionConjunctiveQueries([cq1, cq2], [z])

        fo_query = ucq.to_fo_query()

        self.assertIsInstance(fo_query, FOQuery)
        self.assertEqual(fo_query.answer_variables, (z,))
        # Formula should be a disjunction
        self.assertIsInstance(fo_query.formula, DisjunctionFormula)
