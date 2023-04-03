from math import inf
from unittest import TestCase

from prototyping_inference_engine.api.query.containment.union_conjunctive_queries_containment import UnionConjunctiveQueriesContainment
from prototyping_inference_engine.backward_chaining.breadth_first_rewriting import BreadthFirstRewriting
from src.prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestBreadthFirstRewriting(TestCase):
    data = (
        {"rules": "q(X); r(Y) :- p(X,Y).",
         "ucq_in": "?() :- q(U), r(U).",
         "limit": 1,
         "ucq_out": "?() :- q(U), r(U); r(U), p(U,V), q(V)."},
        {"rules": "q(X); r(Y) :- p(X,Y).",
         "ucq_in": "?() :- q(U), r(U).",
         "limit": 2,
         "ucq_out": "?() :- q(U), r(U); r(U), p(U,V), q(V); r(U), p(U,V), p(V,W), q(W); "
                    "r(U), p(U,V), p(V,W), p(W,T), q(T)."},
        {"rules": "g(X); r(X) :- v(X).",
         "ucq_in": "?() :- g(a); r(a).",
         "ucq_out": "?() :- g(a); r(a); v(a)."},
        {"rules": "g(X); r(X) :- v(X).",
         "ucq_in": "?() :- g(a); r(b).",
         "ucq_out": "?() :- g(a); r(b)."},
        {"rules": "g(X); r(X) :- v(X).",
         "ucq_in": "?() :- g(a); (r(U), t(U)).",
         "ucq_out": "?() :- g(a);  (r(U), t(U)); t(a), v(a)."},
        {"rules": "g(X,X) :- v(X).",
         "ucq_in": "?(X,Y) :- g(X,Y).",
         "ucq_out": "?(X,Y) :- g(X,Y); v(X), X=Y."},
        {"rules": "g(X,X); r(X,Y) :- v(X,Y).",
         "ucq_in": "?(X,Y) :- g(X,Y); r(X,Y), t(X,Y).",
         "ucq_out": "?(X,Y) :- g(X,Y); r(X,Y), t(X,Y); t(X,X), v(X,X), X=Y."},
        {"rules": "g(X,a); r(X,Y) :- v(X,Y).",
         "ucq_in": "?(X,Y) :- g(X,Y); r(X,Y), t(X,Y).",
         "ucq_out": "?(X,Y) :- g(X,Y); r(X,Y), t(X,Y); t(X,a), v(X,a), Y=a."},
        )

    def test_rewrite(self):
        containment = UnionConjunctiveQueriesContainment()
        rewriter = BreadthFirstRewriting()
        for d in self.data:
            rules = set(Dlgp2Parser.instance().parse_rules(d["rules"]))
            ucq_in = next(iter(Dlgp2Parser.instance().parse_union_conjunctive_queries(d["ucq_in"])))
            ucq_out = next(iter(Dlgp2Parser.instance().parse_union_conjunctive_queries(d["ucq_out"])))
            result = rewriter.rewrite(ucq_in, rules, d["limit"] if "limit" in d else inf)
            # print(result)
            # print(ucq_out)
            # print()
            self.assertTrue(containment.is_equivalent_to(result, ucq_out))
