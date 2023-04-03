from unittest import TestCase

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.backward_chaining.unifier.disjunctive_piece_unifier_algorithm import DisjunctivePieceUnifierAlgorithm
from src.prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestDisjunctivePieceUnifierAlgorithm(TestCase):
    data = (
        {"rule": "q(X); r(Y) :- p(X,Y).",
         "query": "?() :- q(U), r(U).",
         "len_dpus": 1},
        {"rule": "g(X); r(X) :- v(X).",
         "query": "?() :- (g(U), e(U,V), g(V)); (r(U), e(U,V), r(V)).",
         "len_dpus": 9},
        {"rule": "g(X); r(X) :- v(X).",
         "query": "?() :- g(a); r(a).",
         "len_dpus": 1},
        {"rule": "g(X); r(X) :- v(X).",
         "query": "?() :- g(a); r(b).",
         "len_dpus": 0},
        {"rule": "g(X); r(X) :- v(X).",
         "query": "?() :- g(a); (r(U), t(U)).",
         "len_dpus": 1},
        {"rule": "hasColor(X, green); hasColor(X, red) :- v(X).",
         "query": "?() :- hasColor(U, T), edge(U,V), hasColor(V, T).",
         "len_dpus": 9},
        )

    def test_compute_disjunctive_unifiers(self):
        for d in self.data:
            rule = next(iter(Dlgp2Parser.instance().parse_rules(d["rule"])))
            query = next(iter(Dlgp2Parser.instance().parse_union_conjunctive_queries(d["query"])))
            dpua = DisjunctivePieceUnifierAlgorithm()
            dpus = dpua.compute_disjunctive_unifiers(query, query, rule)
            #print(*dpus, sep="\n")
            self.assertEqual(len(dpus), d["len_dpus"])
            self.assertTrue(all(dpu.rule == rule for dpu in dpus))
            self.assertTrue(all(Rule.extract_conjunctive_rule(rule, i) == pu.rule for dpu in dpus
                                for i, pu in enumerate(dpu.piece_unifiers)))
