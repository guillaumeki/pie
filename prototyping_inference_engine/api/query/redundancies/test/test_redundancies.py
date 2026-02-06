from unittest import TestCase

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_conjunctive_query import (
    RedundanciesCleanerConjunctiveQuery,
)
from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_union_conjunctive_queries import (
    RedundanciesCleanerUnionConjunctiveQueries,
)
from prototyping_inference_engine.api.query.union_conjunctive_queries import (
    UnionConjunctiveQueries,
)
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.io.parsers.dlgp.dlgp2_parser import Dlgp2Parser


class TestRedundanciesCleanerConjunctiveQuery(TestCase):
    def setUp(self):
        self.cleaner = RedundanciesCleanerConjunctiveQuery.instance()

    def test_singleton_instance(self):
        """Test that instance() returns singleton."""
        c1 = RedundanciesCleanerConjunctiveQuery.instance()
        c2 = RedundanciesCleanerConjunctiveQuery.instance()
        self.assertIs(c1, c2)

    def test_compute_core_no_redundancy(self):
        """Test compute_core on query with no redundant atoms."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y,Z).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        core = self.cleaner.compute_core(cq)
        # All atoms should be preserved (none redundant)
        self.assertEqual(len(core.atoms), 2)
        self.assertEqual(core.answer_variables, (x,))

    def test_compute_core_removes_redundant_atom(self):
        """Test compute_core removes redundant atoms.

        ?(X) :- p(X,Y), p(X,Z) where Y and Z are existential
        One of the p atoms is redundant.
        """
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), p(X,Z).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        core = self.cleaner.compute_core(cq)
        # One of the p(X,_) atoms should be removed as redundant
        self.assertEqual(len(core.atoms), 1)

    def test_compute_cover_removes_more_specific(self):
        """Test compute_cover removes more specific CQs.

        CQ1: ?(X) :- p(X,Y), q(Y)  (more specific)
        CQ2: ?(X) :- p(X,Y)        (more general)
        Cover should only contain CQ2.
        """
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms1, [x])  # More specific
        cq2 = ConjunctiveQuery(atoms2, [x])  # More general
        cover = self.cleaner.compute_cover({cq1, cq2})
        # Only the more general query should remain
        self.assertEqual(len(cover), 1)
        # The remaining CQ should be equivalent to cq2
        remaining = next(iter(cover))
        self.assertEqual(len(remaining.atoms), 1)

    def test_compute_cover_keeps_incomparable(self):
        """Test compute_cover keeps incomparable CQs."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("q(X).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        cover = self.cleaner.compute_cover({cq1, cq2})
        # Both should remain since they are incomparable
        self.assertEqual(len(cover), 2)

    def test_compute_cover_without_core_computation(self):
        """Test compute_cover with del_redundancies_in_cqs=False."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y).")
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        cover = self.cleaner.compute_cover({cq1, cq2}, del_redundancies_in_cqs=False)
        self.assertEqual(len(cover), 1)

    def test_remove_more_specific_than(self):
        """Test remove_more_specific_than removes CQs contained in reference set."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y).")  # More specific
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")  # More general
        atoms3 = Dlgp2Parser.instance().parse_atoms("r(X).")  # Incomparable
        x = Variable("X")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        cq3 = ConjunctiveQuery(atoms3, [x])

        # Remove from {cq1, cq3} those contained in {cq2}
        result = self.cleaner.remove_more_specific_than({cq1, cq3}, {cq2})
        # cq1 is contained in cq2, so it should be removed
        # cq3 is not contained in cq2, so it should remain
        self.assertEqual(len(result), 1)
        self.assertIn(cq3, result)


class TestRedundanciesCleanerUnionConjunctiveQueries(TestCase):
    def setUp(self):
        self.cleaner = RedundanciesCleanerUnionConjunctiveQueries.instance()

    def test_singleton_instance(self):
        """Test that instance() returns singleton."""
        c1 = RedundanciesCleanerUnionConjunctiveQueries.instance()
        c2 = RedundanciesCleanerUnionConjunctiveQueries.instance()
        self.assertIs(c1, c2)

    def test_compute_cover(self):
        """Test compute_cover on UCQ."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y).")  # More specific
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")  # More general
        x = Variable("X")
        z = Variable("Z")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        ucq = UnionConjunctiveQueries([cq1, cq2], [z])

        cover = self.cleaner.compute_cover(ucq)
        # Only the more general CQ should remain
        self.assertEqual(len(cover), 1)
        self.assertIsInstance(cover, UnionQuery)
        self.assertEqual(cover.answer_variables, (z,))

    def test_compute_cover_preserves_label(self):
        """Test that compute_cover preserves the UCQ label."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X).")
        x = Variable("X")
        cq = ConjunctiveQuery(atoms, [x])
        ucq = UnionConjunctiveQueries([cq], [Variable("Z")], label="test_label")

        cover = self.cleaner.compute_cover(ucq)
        self.assertEqual(cover.label, "test_label")

    def test_remove_more_specific_than(self):
        """Test remove_more_specific_than on UCQs."""
        atoms1 = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(Y).")  # More specific
        atoms2 = Dlgp2Parser.instance().parse_atoms("p(X,Y).")  # More general
        atoms3 = Dlgp2Parser.instance().parse_atoms("r(X).")  # Incomparable
        x = Variable("X")
        z = Variable("Z")
        cq1 = ConjunctiveQuery(atoms1, [x])
        cq2 = ConjunctiveQuery(atoms2, [x])
        cq3 = ConjunctiveQuery(atoms3, [x])

        ucq1 = UnionConjunctiveQueries([cq1, cq3], [z])
        ucq2 = UnionConjunctiveQueries([cq2], [z])

        result = self.cleaner.remove_more_specific_than(ucq1, ucq2)
        # cq1 is contained in cq2, so it should be removed
        # cq3 is not contained in cq2, so it should remain
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, UnionQuery)
