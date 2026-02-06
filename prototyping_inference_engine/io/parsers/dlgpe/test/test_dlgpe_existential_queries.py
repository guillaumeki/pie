"""
Additional DLGPE query tests for existential defaults and UCQ conversion.
"""

import unittest

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.io.parsers.dlgpe.conversions import fo_query_to_ucq


class TestDlgpeQueryExistentials(unittest.TestCase):
    """Test DLGPE queries with implicit existential variables."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_query_adds_existential_for_non_answers(self):
        """Non-answer free variables are existentially quantified."""
        result = self.parser.parse("?(X) :- p(X,Y).")
        query = result["queries"][0]

        self.assertEqual(len(query.answer_variables), 1)
        self.assertEqual(str(query.answer_variables[0]), "X")

        self.assertIsInstance(query.formula, ExistentialFormula)
        self.assertEqual(query.formula.free_variables, frozenset({Variable("X")}))
        self.assertIn(Variable("Y"), query.formula.bound_variables)

    def test_query_with_star_keeps_all_free_variables(self):
        """Star makes all free variables answers, no existentials added."""
        result = self.parser.parse("?(*) :- p(X,Y).")
        query = result["queries"][0]

        self.assertEqual(
            query.formula.free_variables,
            frozenset({Variable("X"), Variable("Y")}),
        )
        self.assertNotIsInstance(query.formula, ExistentialFormula)

    def test_query_disjunction_with_existentials(self):
        """Existential variables wrap disjunctive bodies too."""
        result = self.parser.parse("?(X) :- p(X,Y) | q(X,Z).")
        query = result["queries"][0]

        self.assertEqual(query.formula.free_variables, frozenset({Variable("X")}))
        self.assertIn(Variable("Y"), query.formula.bound_variables)
        self.assertIn(Variable("Z"), query.formula.bound_variables)


class TestDlgpeConversions(unittest.TestCase):
    """Test DLGPE FOQuery conversion helpers with existentials."""

    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_fo_query_to_ucq_with_existential(self):
        """Existentially-quantified FOQuery converts to a single CQ."""
        result = self.parser.parse("?(X) :- p(X,Y).")
        query = result["queries"][0]

        ucq = fo_query_to_ucq(query)
        self.assertEqual(len(ucq.conjunctive_queries), 1)

        cq = next(iter(ucq.conjunctive_queries))
        self.assertEqual(len(cq.atoms), 1)

        atom = next(iter(cq.atoms))
        self.assertEqual(atom.predicate.name, "p")
        self.assertEqual(str(atom.terms[0]), "X")
        self.assertEqual(str(atom.terms[1]), "Y")

    def test_fo_query_to_ucq_with_disjunction(self):
        """Disjunctive FOQuery converts to a multi-CQ UCQ."""
        result = self.parser.parse("?(X) :- p(X,Y) | q(X,Y).")
        query = result["queries"][0]

        ucq = fo_query_to_ucq(query)
        self.assertEqual(len(ucq.conjunctive_queries), 2)
        predicates = {
            next(iter(cq.atoms)).predicate.name for cq in ucq.conjunctive_queries
        }
        self.assertEqual(predicates, {"p", "q"})


if __name__ == "__main__":
    unittest.main()
