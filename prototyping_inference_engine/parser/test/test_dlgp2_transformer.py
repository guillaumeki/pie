from unittest import TestCase
from lark import Lark, Tree, Token

from src.prototyping_inference_engine.parser.dlgp.dlgp2_transformer import Dlgp2Transformer


class TestDlgp2Transformer(TestCase):
    examples = ("""@facts
        [f1] p(a), relatedTo(a,b), q(b).
        [f2] p(X), t(X,a,b), s(a,z).
        t(X,a,b), relatedTo(Y,z).
        @constraints
        [c1] ! :- relatedTo(X,X).
        [constraint_2] ! :- X=Y, t(X,Y,b).
        ! :- p(X), q(X).
        @rules
        [r1] relatedTo(X,Y) :- p(X), t(X,Z).
        s(X,Y), s(Y,Z) :- q(X),t(X,Z).
        [rA 1] p(X) :- q(X).
        Y=Z :- t(X,Y),t(X,Z).
        s(a) :- .
        s(Z) :- a=b, X=Y, X=a, p(X,Y).
        <G>(X); <R>(X) :- <V>(X).
        <s1>(Y); <s2>(X) :- p(X,Y).
        @queries
        [q1] ? (X) :- p(X), relatedTo(X,Z), t(a,Z).
        [Query2] ? (X,Y) :- relatedTo(X,X), Y=a.
        ? :- p(X).
        ? :- p(X); q(Y).
        ? (X) :- p(X); q(X).
        ?() :- .""",)
    parsing_results = []
    parser = Lark.open("../dlgp/dlgp2.lark", rel_to=__file__, parser="lalr", transformer=Dlgp2Transformer())

    def setUp(self) -> None:
        self.parsing_results = []
        for e in self.examples:
            self.parsing_results.append(self.parser.parse(e))
            print(self.parsing_results[-1])

    def test_base_properties(self):
        for r in self.parsing_results:
            self.assertIn('body', r)
            self.assertIn('header', r)

    def __test_no_tree_no_token(self, t):
        self.assertNotIsInstance(t, Tree)
        self.assertNotIsInstance(t, Token)
        if isinstance(t, dict):
            for v in t.values():
                self.__test_no_tree_no_token(v)
        if isinstance(t, list) or isinstance(t, tuple) or isinstance(t, set) or isinstance(t, frozenset):
            for v in t:
                self.__test_no_tree_no_token(v)

    def test_no_tree_no_token(self):
        for r in self.parsing_results:
            self.__test_no_tree_no_token(r)
