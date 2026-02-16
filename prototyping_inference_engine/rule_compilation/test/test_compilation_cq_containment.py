import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate, SpecialPredicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.rule_compilation.compilation_cq_containment import (
    CompilationAwareCQContainment,
)
from prototyping_inference_engine.rule_compilation.no_compilation import NoCompilation


class TestCompilationAwareCQContainment(unittest.TestCase):
    def setUp(self) -> None:
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")

    def test_inconsistent_equalities_are_contained(self) -> None:
        equality = Atom(SpecialPredicate.EQUALITY.value, Constant("a"), Constant("b"))
        q1 = ConjunctiveQuery([Atom(self.p, self.x), equality], [self.x])
        q2 = ConjunctiveQuery([Atom(self.p, self.x)], [self.x])
        checker = CompilationAwareCQContainment(NoCompilation())
        self.assertTrue(checker.is_contained_in(q1, q2))

    def test_answer_variable_mismatch_returns_false(self) -> None:
        q1 = ConjunctiveQuery([Atom(self.p, self.x)], [self.x])
        q2 = ConjunctiveQuery(
            [Atom(self.p, self.x), Atom(self.q, self.y)], [self.x, self.y]
        )
        checker = CompilationAwareCQContainment(NoCompilation())
        self.assertFalse(checker.is_contained_in(q1, q2))

    def test_equivalent_queries_are_contained(self) -> None:
        q1 = ConjunctiveQuery([Atom(self.p, self.x)], [self.x])
        q2 = ConjunctiveQuery([Atom(self.p, self.x)], [self.x])
        checker = CompilationAwareCQContainment(NoCompilation())
        self.assertTrue(checker.is_equivalent_to(q1, q2))


if __name__ == "__main__":
    unittest.main()
