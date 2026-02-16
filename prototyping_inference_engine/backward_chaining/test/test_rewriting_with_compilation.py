from unittest import TestCase

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.query.containment.union_conjunctive_queries_containment import (
    UnionConjunctiveQueriesContainment,
)
from prototyping_inference_engine.backward_chaining.breadth_first_rewriting import (
    BreadthFirstRewriting,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.io.parsers.dlgpe.conversions import fo_query_to_ucq
from prototyping_inference_engine.rule_compilation.hierarchical.hierarchical_rule_compilation import (
    HierarchicalRuleCompilation,
)
from prototyping_inference_engine.rule_compilation.id.id_rule_compilation import (
    IDRuleCompilation,
)


def _parse_ucq(text: str):
    query = next(iter(DlgpeParser.instance().parse_queries(text)))
    return fo_query_to_ucq(query)


class TestRewritingWithIDCompilation(TestCase):
    data = (
        {
            "rules": "p(X) :- pp(X). pp(X) :- ppp(X). ppp(Y), q(X,Y) :- r(X).",
            "ucq_in": "?(X) :- q(X,Y), p(Y).",
            "ucq_out": "?(X) :- q(X,Y), p(Y) | r(X).",
        },
        {
            "rules": "t(X,Z) :- s(X,Y), s(Y,Z). s(X,Z) :- q(X,Y), q(Y,Z).",
            "ucq_in": "?(X,Y) :- t(X,Y).",
            "ucq_out": "?(X,Y) :- t(X,Y) | s(X,U), s(U,Y) | q(X,V), q(V,U), s(U,Y) | "
            "s(X,U), q(U,V), q(V,Y) | q(X,V), q(V,U), q(U,W), q(W,Y).",
        },
        {
            "rules": "t(X,Y) :- s(X,Y).",
            "ucq_in": "?(X,Y) :- t(X,Y), t(Y,X), q(X,Y).",
            "ucq_out": "?(X,Y) :- t(X,Y), t(Y,X), q(X,Y).",
        },
        {
            "rules": "p(X,Y) :- q(X,Y).",
            "ucq_in": "?() :- p(a,X), p(X,b).",
            "ucq_out": "?() :- p(a,X), p(X,b).",
        },
        {
            "rules": "p(b,X) :- q(b). p(a,X) :- q(a).",
            "ucq_in": "?(X) :- p(X,Y), p(X,Z).",
            "ucq_out": "?(X) :- p(X,Y), p(X,Z) | q(b), X=b | q(a), X=a.",
        },
        {
            "rules": "r(X,Y,X) :- p(X,Y).",
            "ucq_in": "?() :- r(U,V,W), r(W,Z,U).",
            "ucq_out": "?() :- r(U,V,W), r(W,Z,U).",
        },
        {
            "rules": "p(X,Y) :- q(X,Y). p(X,X) :- q(X,Y).",
            "ucq_in": "?(X,Y) :- p(X,Y).",
            "ucq_out": "?(X,Y) :- p(X,Y).",
        },
    )

    def test_rewrite_with_id_compilation(self):
        containment = UnionConjunctiveQueriesContainment()
        for case in self.data:
            rules = set(DlgpeParser.instance().parse_rules(case["rules"]))
            rule_base = RuleBase(rules)
            compilation = IDRuleCompilation()
            compilation.compile(rule_base)

            rewriter = BreadthFirstRewriting(rule_compilation=compilation)
            result = rewriter.rewrite(_parse_ucq(case["ucq_in"]), rule_base.rules)
            expected = _parse_ucq(case["ucq_out"])

            self.assertTrue(containment.is_equivalent_to(result, expected))


class TestRewritingWithHierarchicalCompilation(TestCase):
    data = (
        {
            "rules": "p(X) :- pp(X). pp(X) :- ppp(X). ppp(Y), q(X,Y) :- r(X).",
            "ucq_in": "?(X) :- q(X,Y), p(Y).",
            "ucq_out": "?(X) :- q(X,Y), p(Y) | r(X).",
        },
        {
            "rules": "t(X,Z) :- s(X,Y), s(Y,Z). s(X,Z) :- q(X,Y), q(Y,Z).",
            "ucq_in": "?(X,Y) :- t(X,Y).",
            "ucq_out": "?(X,Y) :- t(X,Y) | s(X,U), s(U,Y) | q(X,V), q(V,U), s(U,Y) | "
            "s(X,U), q(U,V), q(V,Y) | q(X,V), q(V,U), q(U,W), q(W,Y).",
        },
        {
            "rules": "t(X,Y) :- s(X,Y).",
            "ucq_in": "?(X,Y) :- t(X,Y), t(Y,X), q(X,Y).",
            "ucq_out": "?(X,Y) :- t(X,Y), t(Y,X), q(X,Y).",
        },
        {
            "rules": "p(X,Y) :- q(X,Y).",
            "ucq_in": "?() :- p(a,X), p(X,b).",
            "ucq_out": "?() :- p(a,X), p(X,b).",
        },
        {
            "rules": "p(b,X) :- q(b). p(a,X) :- q(a).",
            "ucq_in": "?(X) :- p(X,Y), p(X,Z).",
            "ucq_out": "?(X) :- p(X,Y), p(X,Z) | q(b), X=b | q(a), X=a.",
        },
        {
            "rules": "r(X,Y,X) :- p(X,Y).",
            "ucq_in": "?() :- r(U,V,W), r(W,Z,U).",
            "ucq_out": "?() :- r(U,V,W), r(W,Z,U) | p(U,Z).",
        },
        {
            "rules": "p(X,Y) :- q(X,Y). p(X,X) :- q(X,Y).",
            "ucq_in": "?(X,Y) :- p(X,Y).",
            "ucq_out": "?(X,Y) :- p(X,Y) | q(X,Z), X=Y.",
        },
    )

    def test_rewrite_with_hierarchical_compilation(self):
        containment = UnionConjunctiveQueriesContainment()
        for case in self.data:
            rules = set(DlgpeParser.instance().parse_rules(case["rules"]))
            rule_base = RuleBase(rules)
            compilation = HierarchicalRuleCompilation()
            compilation.compile(rule_base)

            rewriter = BreadthFirstRewriting(rule_compilation=compilation)
            result = rewriter.rewrite(_parse_ucq(case["ucq_in"]), rule_base.rules)
            expected = _parse_ucq(case["ucq_out"])

            self.assertTrue(containment.is_equivalent_to(result, expected))
