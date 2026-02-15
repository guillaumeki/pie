from unittest import TestCase

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.unifier.piece_unifier import (
    PieceUnifier,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.io.parsers.dlgpe.conversions import (
    try_convert_fo_query,
)


def _parse_cq(text: str) -> ConjunctiveQuery:
    query = next(iter(DlgpeParser.instance().parse_queries(text)))
    converted = try_convert_fo_query(query)
    if not isinstance(converted, ConjunctiveQuery):
        raise AssertionError("Expected conjunctive query conversion to succeed.")
    return converted


class TestPieceUnifier(TestCase):
    data = (
        {
            "piece_unifier": PieceUnifier(
                rule=next(
                    iter(DlgpeParser.instance().parse_rules("r(X,Y), q(Y) :- p(X)."))
                ),
                query=_parse_cq("?() :- r(U,V), q(V), r(U,U)."),
                unified_query_part=FrozenAtomSet(
                    DlgpeParser.instance().parse_atoms("r(U, V), q(V).")
                ),
                partition=TermPartition(
                    [{Variable("U"), Variable("X")}, {Variable("V"), Variable("Y")}]
                ),
            ),
            "separating_variables": {Variable("U")},
        },
    )

    def test_associated_substitution(self):
        pass

    def test_is_compatible_with(self):
        pass

    def test_aggregate(self):
        pass

    def test_separating_variables(self):
        for d in self.data:
            self.assertEqual(
                d["piece_unifier"].separating_variables, d["separating_variables"]
            )

    def test_sticky_variables(self):
        pass
