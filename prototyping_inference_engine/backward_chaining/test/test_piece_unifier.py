from unittest import TestCase

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.backward_chaining.unifier.piece_unifier import PieceUnifier
from src.prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestPieceUnifier(TestCase):
    data = ({
        "piece_unifier": PieceUnifier(rule=next(iter(Dlgp2Parser.instance().parse_rules("r(X,Y), q(Y) :- p(X)."))),
        query=next(iter(Dlgp2Parser.instance().parse_conjunctive_queries("?() :- r(U,V), q(V), r(U,U)."))),
        unified_query_part=FrozenAtomSet(Dlgp2Parser.instance().parse_atoms("r(U, V), q(V).")),
        partition=TermPartition([{Variable("U"), Variable("X")}, {Variable("V"), Variable("Y")}])),
        "separating_variables": {Variable("U")} },
    )

    def test_associated_substitution(self):
        pass

    def test_is_compatible_with(self):
        pass

    def test_aggregate(self):
        pass

    def test_separating_variables(self):
        for d in self.data:
            self.assertEqual(d["piece_unifier"].separating_variables, d["separating_variables"])

    def test_sticky_variables(self):
        pass
