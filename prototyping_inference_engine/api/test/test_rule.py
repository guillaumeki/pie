from typing import Callable
from unittest import TestCase

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from src.prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestRule(TestCase):
    disjunctive_rules = Dlgp2Parser.instance().parse_rules("""
        <G>(X); <R>(X) :- <V>(X).
        <s1>(Y); <s2>(X) :- p(X,Y).
        <s1>(Y), <s3>(X,Y); <s2>(X), <s5>(X,Y) :- p(X,Y).""")

    conjonctive_rules = Dlgp2Parser.instance().parse_rules("""
        <G>(X) :- <V>(X).
        <s1>(Y) :- p(X,Y).
        s(X,Y), s(Y,Z) :- q(X),t(X,Z).""")

    @classmethod
    def check_on_disjunctive_rules(cls, fun: Callable[[Rule], None]):
        for r in cls.disjunctive_rules:
            fun(r)

    @classmethod
    def check_on_conjunctive_rules(cls, fun: Callable[[Rule], None]):
        for r in cls.conjonctive_rules:
            fun(r)

    def test_frontier(self):
        def test_frontier(rule, *args):
            body_variables = set(rule.body.variables)
            head_variables = set(v for h in rule.head for v in h.variables)
            frontier_variables = body_variables & head_variables
            self.assertEqual(frontier_variables, rule.frontier)
        self.check_on_conjunctive_rules(test_frontier)
        self.check_on_disjunctive_rules(test_frontier)

    def test_is_conjunctive(self):
        self.check_on_conjunctive_rules(lambda rule, *args: self.assertTrue(rule.is_conjunctive))
        self.check_on_disjunctive_rules(lambda rule, *args: self.assertFalse(rule.is_conjunctive))

    """def test_body(self):
        self.fail()

    def test_head(self):
        self.fail()

    def test_label(self):
        self.fail()"""