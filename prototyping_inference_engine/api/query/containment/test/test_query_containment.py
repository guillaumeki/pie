from unittest import TestCase

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import (
    ConjunctiveQueryContainment,
    HomomorphismBasedCQContainment,
)
from prototyping_inference_engine.api.query.containment.union_conjunctive_queries_containment import (
    UnionConjunctiveQueriesContainment,
)
from prototyping_inference_engine.api.query.union_conjunctive_queries import (
    UnionConjunctiveQueries,
)
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestConjunctiveQueryContainment(TestCase):
    def setUp(self):
        self.containment = HomomorphismBasedCQContainment.instance()

    def test_singleton_instance(self):
        """Test that instance() returns singleton."""
        c1 = HomomorphismBasedCQContainment.instance()
        c2 = HomomorphismBasedCQContainment.instance()
        self.assertIs(c1, c2)

    def test_is_conjunctive_query_containment(self):
        """Test that HomomorphismBasedCQContainment implements the protocol."""
        self.assertIsInstance(self.containment, ConjunctiveQueryContainment)

    def test_identical_queries_contained(self):
        """Test that identical queries are contained in each other."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        self.assertTrue(self.containment.is_contained_in(cq, cq))

    def test_more_specific_contained_in_more_general(self):
        """Test that a more specific query is contained in more general.

        Q1: ?(X) :- p(X,Y), q(Y), r(Y)  (more atoms = more specific)
        Q2: ?(X) :- p(X,Y), q(Y)        (fewer atoms = more general)
        Q1 is contained in Q2
        """
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y), r(Y).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        self.assertTrue(self.containment.is_contained_in(cq1, cq2))
        self.assertFalse(self.containment.is_contained_in(cq2, cq1))

    def test_different_answer_variable_count_not_contained(self):
        """Test that queries with different answer variable counts are not contained."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x, y])
        self.assertFalse(self.containment.is_contained_in(cq1, cq2))
        self.assertFalse(self.containment.is_contained_in(cq2, cq1))

    def test_disjoint_predicates_not_contained(self):
        """Test that queries with disjoint predicates are not contained."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(X).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        self.assertFalse(self.containment.is_contained_in(cq1, cq2))
        self.assertFalse(self.containment.is_contained_in(cq2, cq1))

    def test_is_equivalent_to(self):
        """Test is_equivalent_to method."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms, [x])
        cq2 = ConjunctiveQuery(atoms, [x])
        self.assertTrue(self.containment.is_equivalent_to(cq1, cq2))

    def test_not_equivalent_when_not_bidirectionally_contained(self):
        """Test queries are not equivalent when not bidirectionally contained."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        self.assertFalse(self.containment.is_equivalent_to(cq1, cq2))

    def test_containment_with_variable_renaming(self):
        """Test containment works with variable renaming.

        Q1: ?(X) :- p(X,Y)
        Q2: ?(A) :- p(A,B)
        These should be equivalent (variable names don't matter)
        """
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(A,B).")
        cq1 = ConjunctiveQuery(atoms1, [Variable("X")])
        cq2 = ConjunctiveQuery(atoms2, [Variable("A")])
        self.assertTrue(self.containment.is_equivalent_to(cq1, cq2))


class TestUnionConjunctiveQueriesContainment(TestCase):
    def setUp(self):
        self.containment = UnionConjunctiveQueriesContainment.instance()

    def test_singleton_instance(self):
        """Test that instance() returns singleton."""
        c1 = UnionConjunctiveQueriesContainment.instance()
        c2 = UnionConjunctiveQueriesContainment.instance()
        self.assertIs(c1, c2)

    def test_identical_ucqs_contained(self):
        """Test that identical UCQs are contained in each other."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        ucq = UnionConjunctiveQueries([cq], [Variable("Z")])
        self.assertTrue(self.containment.is_contained_in(ucq, ucq))

    def test_subset_ucq_contained(self):
        """Test that UCQ with subset of CQs is contained."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq1 = UnionConjunctiveQueries([cq1], [z])  # Just cq1
        ucq2 = UnionConjunctiveQueries([cq1, cq2], [z])  # Both cq1 and cq2
        self.assertTrue(self.containment.is_contained_in(ucq1, ucq2))

    def test_superset_ucq_not_contained_in_subset(self):
        """Test that UCQ with more CQs is not contained in one with fewer."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(Y).")
        x = Variable("X")
        y = Variable("Y")
        z = Variable("Z")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [y])
        ucq1 = UnionConjunctiveQueries([cq1], [z])
        ucq2 = UnionConjunctiveQueries([cq1, cq2], [z])
        # ucq2 is NOT contained in ucq1 because cq2 has no containing CQ in ucq1
        self.assertFalse(self.containment.is_contained_in(ucq2, ucq1))

    def test_different_answer_variable_count_not_contained(self):
        """Test that UCQs with different answer variable counts are not contained."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        y = Variable("Y")
        cq1 = ConjunctiveQuery(atoms, [x])
        cq2 = ConjunctiveQuery(atoms, [x, y])
        ucq1 = UnionConjunctiveQueries([cq1], [Variable("Z")])
        ucq2 = UnionConjunctiveQueries([cq2], [Variable("Z"), Variable("W")])
        self.assertFalse(self.containment.is_contained_in(ucq1, ucq2))

    def test_is_equivalent_to(self):
        """Test is_equivalent_to method."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        z = Variable("Z")
        ucq1 = UnionConjunctiveQueries([cq], [z])
        ucq2 = UnionConjunctiveQueries([cq], [z])
        self.assertTrue(self.containment.is_equivalent_to(ucq1, ucq2))

    def test_empty_ucq_contained_in_any(self):
        """Test that empty UCQ is contained in any UCQ."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        z = Variable("Z")
        empty_ucq = UnionConjunctiveQueries([], [z])
        non_empty_ucq = UnionConjunctiveQueries([cq], [z])
        # Empty UCQ vacuously satisfies: all CQs in empty_ucq are contained
        self.assertTrue(self.containment.is_contained_in(empty_ucq, non_empty_ucq))
        self.assertTrue(self.containment.is_contained_in(empty_ucq, empty_ucq))
