"""Port of Integraal backward-chaining QueryCoreProcessor tests."""

from unittest import TestCase

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import (
    HomomorphismBasedCQContainment,
)
from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_conjunctive_query import (
    RedundanciesCleanerConjunctiveQuery,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestQueryCoreProcessorPort(TestCase):
    def setUp(self) -> None:
        self.parser = DlgpeParser.instance()
        self.cleaner = RedundanciesCleanerConjunctiveQuery.instance()
        self.containment = HomomorphismBasedCQContainment.instance()

    def test_query_core_with_constants(self) -> None:
        query_atoms = self.parser.parse_atoms(
            "p(a,X), p(Y,X), p(Y,Z), p(V,Z), p(V,U), p(b,U), "
            "p(a,X2), p(X2,c), p(b,X2), p(a,X1), p(X1,c), p(b,X1)."
        )
        expected_atoms = self.parser.parse_atoms("p(a,X), p(b,X), p(X,c).")

        query = ConjunctiveQuery(query_atoms, [])
        expected = ConjunctiveQuery(expected_atoms, [])

        result = self.cleaner.compute_core(query)

        self.assertEqual(len(result.atoms), len(expected.atoms))
        self.assertTrue(self.containment.is_equivalent_to(result, expected))

    def test_query_core_with_frozen_answer_variables(self) -> None:
        a = Variable("A")
        b = Variable("B")
        c = Variable("C")

        query_atoms = self.parser.parse_atoms(
            "p(A,X), p(Y,X), p(Y,Z), p(V,Z), p(V,U), p(B,U), "
            "p(A,X2), p(X2,C), p(B,X2), p(A,X1), p(X1,C), p(B,X1)."
        )
        expected_atoms = self.parser.parse_atoms("p(A,X), p(B,X), p(X,C).")

        query = ConjunctiveQuery(query_atoms, [a, b, c])
        expected = ConjunctiveQuery(expected_atoms, [a, b, c])

        result = self.cleaner.compute_core(query)

        self.assertEqual(len(result.atoms), len(expected.atoms))
        self.assertTrue(self.containment.is_equivalent_to(result, expected))
