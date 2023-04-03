from unittest import TestCase

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries
from src.prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestDlgp2Parser(TestCase):
    def test_parse_atoms(self):
        atoms_str = "p(a), relatedTo(a,b), q(b). [f2] p(X), t(X,a,b), s(a,z), p(a)."
        #print(Dlgp2Parser.instance().parse_atoms(atoms_str))

    def test_parse_union_conjunctive_queries(self):
        tests = (
            {"to_parse": "?() :- q(U), r(U).",
             "ucqs": {UnionConjunctiveQueries(
                        [ConjunctiveQuery(
                            FrozenAtomSet(Dlgp2Parser.instance().parse_atoms("q(U), r(U).")))])}},
            {"to_parse": "?() :- (g(U), e(U,V), g(V)); (r(U), e(U,V), r(V)).",
             "ucqs": {UnionConjunctiveQueries([
                 ConjunctiveQuery(FrozenAtomSet(Dlgp2Parser.instance().parse_atoms("g(U), e(U,V), g(V)."))),
                 ConjunctiveQuery(FrozenAtomSet(Dlgp2Parser.instance().parse_atoms("r(U), e(U,V), r(V).")))
             ])}}
            ,)
        for test in tests:
            ucq = set(Dlgp2Parser.instance().parse_union_conjunctive_queries(test["to_parse"]))
            self.assertEqual(test["ucqs"], ucq)
