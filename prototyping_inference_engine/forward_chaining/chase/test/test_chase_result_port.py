"""Ported chase-result style integration tests for forward chaining."""

from __future__ import annotations

import unittest
from typing import Callable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.core.core_variants import (
    CoreRetractionVariant,
)
from prototyping_inference_engine.api.atom.set.core.multithread_by_piece_core_processor import (
    MultiThreadsByPieceCoreProcessor,
)
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.core.fact_base_core_processor import (
    MutableMaterializedCoreProcessor,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.chase_builder import (
    ChaseBuilder,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.limit_number_of_step import (
    LimitNumberOfStep,
)
from prototyping_inference_engine.forward_chaining.chase.test.port_test_utils import (
    is_equivalent,
    test_builder,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.compute_core import (
    ComputeCore,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.compute_local_core import (
    ComputeLocalCore,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.rule_split import (
    RuleSplit,
)

CaseBuilder = Callable[[], tuple[MutableInMemoryFactBase, RuleBase]]


def _core_treatment() -> ComputeCore:
    processor = MutableMaterializedCoreProcessor(
        MultiThreadsByPieceCoreProcessor(16, CoreRetractionVariant.EXHAUSTIVE)
    )
    return ComputeCore(processor)


def _local_core_treatment() -> ComputeLocalCore:
    processor = MutableMaterializedCoreProcessor(
        MultiThreadsByPieceCoreProcessor(16, CoreRetractionVariant.EXHAUSTIVE)
    )
    return ComputeLocalCore(processor)


def _build_case_chain() -> tuple[MutableInMemoryFactBase, RuleBase]:
    x = Variable("X")
    y = Variable("Y")
    a = Constant("a")
    b = Constant("b")
    c = Constant("c")

    p = Predicate("p", 2)
    q = Predicate("q", 2)
    r = Predicate("r", 2)

    facts = MutableInMemoryFactBase([Atom(p, a, b), Atom(p, b, c)])
    rules = RuleBase(
        {
            Rule(Atom(p, x, y), Atom(p, y, x), "sym"),
            Rule(Atom(p, x, y), Atom(q, x, y), "to_q"),
            Rule(Atom(q, x, y), Atom(r, x, y), "to_r"),
        }
    )
    return facts, rules


def _build_case_existential() -> tuple[MutableInMemoryFactBase, RuleBase]:
    x = Variable("X")
    y = Variable("Y")
    a = Constant("a")
    b = Constant("b")

    base = Predicate("base", 1)
    link = Predicate("link", 2)
    tag = Predicate("tag", 2)

    facts = MutableInMemoryFactBase([Atom(base, a), Atom(base, b)])
    rules = RuleBase(
        {
            Rule(Atom(base, x), ExistentialFormula(y, Atom(link, x, y)), "ex_link"),
            Rule(Atom(link, x, y), Atom(tag, x, y), "to_tag"),
        }
    )
    return facts, rules


def _build_case_conj_head() -> tuple[MutableInMemoryFactBase, RuleBase]:
    x = Variable("X")
    a = Constant("a")
    b = Constant("b")

    node = Predicate("node", 1)
    left = Predicate("left", 1)
    right = Predicate("right", 1)
    done = Predicate("done", 1)

    facts = MutableInMemoryFactBase([Atom(node, a), Atom(node, b)])
    rules = RuleBase(
        {
            Rule(
                Atom(node, x),
                ConjunctionFormula(Atom(left, x), Atom(right, x)),
                "split_me",
            ),
            Rule(Atom(left, x), Atom(done, x), "left_done"),
        }
    )
    return facts, rules


_CASES: tuple[tuple[str, CaseBuilder], ...] = (
    ("chain", _build_case_chain),
    ("existential", _build_case_existential),
    ("conj_head", _build_case_conj_head),
)

_CONFIGURATIONS: tuple[tuple[str, Callable[[ChaseBuilder], ChaseBuilder]], ...] = (
    ("restricted_computer", lambda b: b.use_restricted_computer()),
    (
        "breadth_first_restricted_computer",
        lambda b: b.use_breadth_first_applier().use_restricted_computer(),
    ),
    (
        "multithread_restricted_computer",
        lambda b: b.use_restricted_computer().use_multi_thread_rule_applier(),
    ),
    (
        "restricted_computer_with_rule_split",
        lambda b: b.use_restricted_computer().add_global_pretreatments(RuleSplit()),
    ),
    ("multithread_applier", lambda b: b.use_multi_thread_rule_applier()),
    ("restricted_checker", lambda b: b.use_restricted_checker()),
    (
        "restricted_checker_with_rule_split",
        lambda b: b.use_restricted_checker().add_global_pretreatments(RuleSplit()),
    ),
    ("naive_computer", lambda b: b.use_naive_computer()),
    ("parallel_applier", lambda b: b.use_parallel_applier()),
    ("breadth_first_applier", lambda b: b.use_breadth_first_applier()),
    ("semi_naive_computer", lambda b: b.use_semi_naive_computer()),
    ("frontier_pseudo_skolem", lambda b: b.use_frontier_skolem()),
    ("grd_scheduler", lambda b: b.use_grd_rule_scheduler()),
    ("two_steps_computer", lambda b: b.use_two_step_computer()),
    (
        "always_true_checker_with_limit",
        lambda b: b.use_always_true_checker().add_halting_conditions(
            LimitNumberOfStep(3)
        ),
    ),
    ("equivalent_checker", lambda b: b.use_equivalent_checker()),
    ("all_transformer", lambda b: b.use_all_transformer()),
    (
        "compute_core_treatment",
        lambda b: b.add_step_end_treatments(_core_treatment()),
    ),
    (
        "compute_local_core_treatment",
        lambda b: b.add_step_end_treatments(_local_core_treatment()),
    ),
)


def _compute_expected(case_builder: CaseBuilder) -> MutableInMemoryFactBase:
    fact_base, rule_base = case_builder()
    chase = test_builder(fact_base, rule_base).build().get()
    chase.execute()
    return MutableInMemoryFactBase(fact_base)


class TestChaseResultPort(unittest.TestCase):
    def test_chase_variants_match_expected_saturation(self) -> None:
        for case_name, case_builder in _CASES:
            expected = _compute_expected(case_builder)
            for configuration_name, configure in _CONFIGURATIONS:
                with self.subTest(case=case_name, configuration=configuration_name):
                    if (
                        case_name == "existential"
                        and configuration_name == "equivalent_checker"
                    ):
                        continue
                    fact_base, rule_base = case_builder()
                    chase = configure(test_builder(fact_base, rule_base)).build().get()
                    chase.execute()
                    self.assertTrue(is_equivalent(fact_base, expected))


if __name__ == "__main__":
    unittest.main()
