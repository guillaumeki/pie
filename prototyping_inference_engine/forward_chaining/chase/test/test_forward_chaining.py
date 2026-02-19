"""Forward chaining tests (ported/adapted from Integraal semantics)."""

from __future__ import annotations

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.evaluable_function_term import (
    EvaluableFunctionTerm,
)
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.chase_builder import (
    ChaseBuilder,
)
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data_impl import (
    ChasableDataImpl,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.limit_number_of_step import (
    LimitNumberOfStep,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.rule_split import (
    RuleSplit,
)


class TestForwardChaining(unittest.TestCase):
    def setUp(self) -> None:
        self.x = Variable("X")
        self.y = Variable("Y")
        self.z = Variable("Z")

        self.p = Predicate("p", 2)
        self.q = Predicate("q", 2)
        self.r = Predicate("r", 1)

    def _base_data(self) -> MutableInMemoryFactBase:
        a = Constant("a")
        b = Constant("b")
        c = Constant("c")
        return MutableInMemoryFactBase(
            [Atom(self.p, a, b), Atom(self.p, b, c), Atom(self.r, a)]
        )

    def _symmetry_rule_base(self) -> RuleBase:
        body = Atom(self.p, self.x, self.y)
        head = Atom(self.p, self.y, self.x)
        return RuleBase({Rule(body, head, "sym")})

    def test_default_chase_reaches_fixpoint(self) -> None:
        fb = self._base_data()
        rb = self._symmetry_rule_base()

        chase = ChaseBuilder.default_chase(fb, rb)
        chase.execute()

        self.assertIn(Atom(self.p, Constant("b"), Constant("a")), fb)

    def test_scheduler_variants(self) -> None:
        for configure in (
            lambda b: b.use_naive_rule_scheduler(),
            lambda b: b.use_grd_rule_scheduler(),
            lambda b: b.use_by_predicate_rule_scheduler(),
        ):
            with self.subTest(configure=configure):
                fb = self._base_data()
                rb = self._symmetry_rule_base()
                chase = configure(ChaseBuilder.default_builder(fb, rb)).build().get()
                chase.execute()
                self.assertIn(Atom(self.p, Constant("b"), Constant("a")), fb)

    def test_rule_applier_variants(self) -> None:
        for configure in (
            lambda b: b.use_parallel_applier(),
            lambda b: b.use_breadth_first_applier(),
            lambda b: b.use_multi_thread_rule_applier(),
        ):
            with self.subTest(configure=configure):
                fb = self._base_data()
                rb = self._symmetry_rule_base()
                chase = configure(ChaseBuilder.default_builder(fb, rb)).build().get()
                chase.execute()
                self.assertIn(Atom(self.p, Constant("b"), Constant("a")), fb)

    def test_trigger_computer_variants(self) -> None:
        for configure in (
            lambda b: b.use_naive_computer(),
            lambda b: b.use_semi_naive_computer(),
            lambda b: b.use_two_step_computer(),
            lambda b: b.use_restricted_computer(),
        ):
            with self.subTest(configure=configure):
                fb = self._base_data()
                rb = self._symmetry_rule_base()
                chase = configure(ChaseBuilder.default_builder(fb, rb)).build().get()
                chase.execute()
                self.assertIn(Atom(self.p, Constant("b"), Constant("a")), fb)

    def test_checker_variants(self) -> None:
        for configure in (
            lambda b: b.use_always_true_checker().add_halting_conditions(
                LimitNumberOfStep(3)
            ),
            lambda b: b.use_oblivious_checker(),
            lambda b: b.use_semi_oblivious_checker(),
            lambda b: b.use_restricted_checker(),
            lambda b: b.use_equivalent_checker(),
            lambda b: b.use_so_restricted_checker(),
        ):
            with self.subTest(configure=configure):
                fb = self._base_data()
                rb = self._symmetry_rule_base()
                chase = configure(ChaseBuilder.default_builder(fb, rb)).build().get()
                chase.execute()
                self.assertIn(Atom(self.p, Constant("b"), Constant("a")), fb)

    def test_rule_split_pretreatment(self) -> None:
        s = Predicate("s", 1)
        t = Predicate("t", 1)
        body = Atom(self.r, self.x)
        head = ConjunctionFormula(Atom(s, self.x), Atom(t, self.x))
        rb = RuleBase({Rule(body, head)})
        fb = MutableInMemoryFactBase([Atom(self.r, Constant("a"))])

        chase = (
            ChaseBuilder.default_builder(fb, rb)
            .add_global_pretreatments(RuleSplit())
            .build()
            .get()
        )
        chase.execute()

        self.assertIn(Atom(s, Constant("a")), fb)
        self.assertIn(Atom(t, Constant("a")), fb)

    def test_existential_renamers(self) -> None:
        e = Predicate("e", 2)
        body = Atom(self.r, self.x)
        head = ExistentialFormula(self.y, Atom(e, self.x, self.y))
        rb = RuleBase({Rule(body, head)})

        configs = (
            lambda b: b.use_fresh_naming(),
            lambda b: b.use_body_skolem(),
            lambda b: b.use_frontier_skolem(),
            lambda b: b.use_frontier_by_piece_skolem(),
            lambda b: b.use_body_true_skolem(),
            lambda b: b.use_frontier_true_skolem(),
            lambda b: b.use_frontier_by_piece_true_skolem(),
        )

        for configure in configs:
            with self.subTest(configure=configure):
                fb = MutableInMemoryFactBase([Atom(self.r, Constant("a"))])
                chase = configure(ChaseBuilder.default_builder(fb, rb)).build().get()
                chase.execute()
                derived = [atom for atom in fb if atom.predicate == e]
                self.assertEqual(1, len(derived))
                self.assertEqual(Constant("a"), derived[0].terms[0])

    def test_stratified_chase(self) -> None:
        s = Predicate("s", 1)
        t = Predicate("t", 1)

        r1 = Rule(Atom(self.r, self.x), Atom(s, self.x))
        r2 = Rule(Atom(s, self.x), Atom(t, self.x))
        rb = RuleBase({r1, r2})
        fb = MutableInMemoryFactBase([Atom(self.r, Constant("a"))])

        stratified = (
            ChaseBuilder.default_builder(ChasableDataImpl(fb), rb)
            .use_stratified_chase()
            .set_strata([RuleBase({r1}), RuleBase({r2})])
            .build()
            .get()
        )
        stratified.execute()

        self.assertIn(Atom(s, Constant("a")), fb)
        self.assertIn(Atom(t, Constant("a")), fb)

    def test_function_term_evaluation_in_head(self) -> None:
        lit_factory = LiteralFactory(DictStorage())
        one = lit_factory.create("1")
        two = lit_factory.create("2")

        num = Predicate("num", 1)
        out = Predicate("out", 1)

        body = Atom(num, self.x)
        head = Atom(out, EvaluableFunctionTerm("stdfct:sum", [self.x, one]))

        rb = RuleBase({Rule(body, head)})
        fb = MutableInMemoryFactBase([Atom(num, two)])

        chase = (
            ChaseBuilder.default_builder(fb, rb)
            .use_naive_rule_scheduler()
            .build()
            .get()
        )
        chase.execute()

        out_atoms = [atom for atom in fb if atom.predicate == out]
        self.assertEqual(1, len(out_atoms))
        produced_term = out_atoms[0].terms[0]
        self.assertIsInstance(produced_term, Literal)
        produced_literal = produced_term
        assert isinstance(produced_literal, Literal)
        self.assertEqual(3, produced_literal.value)


if __name__ == "__main__":
    unittest.main()
