from unittest import TestCase

from prototyping_inference_engine.backward_chaining.rewriting_operator.without_aggregation_rewriting_operator import \
    WithoutAggregationRewritingOperator
from src.prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestWithoutAggregationRewritingOperator(TestCase):
    data = (
        {"rules": "q(X); r(Y) :- p(X,Y).",
         "query": "?() :- q(U), r(U).",
         "len_ucq": 1},
        {"rules": "g(X); r(X) :- v(X).",
         "query": "?() :- (g(U), e(U,V), g(V)); (r(U), e(U,V), r(V)).",
         "len_ucq": 9},
        {"rules": "g(X); r(X) :- v(X).",
         "query": "?() :- g(a); r(a).",
         "len_ucq": 1},
        {"rules": "g(X); r(X) :- v(X).",
         "query": "?() :- g(a); r(b).",
         "len_ucq": 0},
        {"rules": "g(X); r(X) :- v(X).",
         "query": "?() :- g(a); (r(U), t(U)).",
         "len_ucq": 1},
        {"rules": "hasColor(X, green); hasColor(X, red) :- v(X).",
         "query": "?() :- hasColor(U, T), edge(U,V), hasColor(V, T).",
         "len_ucq": 9},
        {"rules": "g(X,X) :- v(X).",
         "query": "?(X,Y) :- g(X,Y).",
         "len_ucq": 1},
        {"rules": "g(X,X); r(X,Y) :- v(X,Y).",
         "query": "?(X,Y) :- g(X,Y); r(X,Y), t(X,Y).",
         "len_ucq": 1},
        {"rules": "g(X,a); r(X,Y) :- v(X,Y).",
         "query": "?(X,Y) :- g(X,Y); r(X,Y), t(X,Y).",
         "len_ucq": 1},
    )

    def test_rewrite(self):
        for d in self.data:
            rewrite = WithoutAggregationRewritingOperator()
            rules = set(Dlgp2Parser.instance().parse_rules(d["rules"]))
            query = next(iter(Dlgp2Parser.instance().parse_union_conjunctive_queries(d["query"])))
            rewriting = rewrite(query, query, rules)
            print(*rewriting, sep="\n", end="\n"*2)
            self.assertEqual(d["len_ucq"], len(rewriting))
