"""Ported compute-local-core treatment tests for forward chaining."""

from __future__ import annotations

import unittest
from typing import Callable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.core.by_piece_and_variable_core_processor import (
    ByPieceAndVariableCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.core.by_piece_core_processor import (
    ByPieceCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.core.core_variants import (
    CoreRetractionVariant,
)
from prototyping_inference_engine.api.atom.set.core.multithread_by_piece_core_processor import (
    MultiThreadsByPieceCoreProcessor,
)
from prototyping_inference_engine.api.atom.set.core.naive_core_processor import (
    NaiveCoreProcessor,
)
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.core.fact_base_core_processor import (
    MutableMaterializedCoreProcessor,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.chase_builder import (
    ChaseBuilder,
)
from prototyping_inference_engine.forward_chaining.chase.test.port_test_utils import (
    is_core,
    is_equivalent,
    test_builder,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.compute_local_core import (
    ComputeLocalCore,
)

_PROCESSOR_FACTORIES: tuple[tuple[str, Callable[[], CoreAlgorithm]], ...] = (
    (
        "mt_by_specialisation",
        lambda: MultiThreadsByPieceCoreProcessor(
            16, CoreRetractionVariant.BY_SPECIALISATION
        ),
    ),
    (
        "mt_by_deletion",
        lambda: MultiThreadsByPieceCoreProcessor(16, CoreRetractionVariant.BY_DELETION),
    ),
    (
        "mt_exhaustive",
        lambda: MultiThreadsByPieceCoreProcessor(16, CoreRetractionVariant.EXHAUSTIVE),
    ),
    (
        "by_piece_specialisation",
        lambda: ByPieceCoreProcessor(CoreRetractionVariant.BY_SPECIALISATION),
    ),
    (
        "by_piece_deletion",
        lambda: ByPieceCoreProcessor(CoreRetractionVariant.BY_DELETION),
    ),
    (
        "by_piece_exhaustive",
        lambda: ByPieceCoreProcessor(CoreRetractionVariant.EXHAUSTIVE),
    ),
    ("naive", lambda: NaiveCoreProcessor()),
    ("by_piece_and_variable", lambda: ByPieceAndVariableCoreProcessor()),
)

_APPLIERS: tuple[tuple[str, Callable[[ChaseBuilder], ChaseBuilder]], ...] = (
    ("parallel", lambda b: b.use_parallel_applier()),
    ("breadth_first", lambda b: b.use_breadth_first_applier()),
)

CaseBuilder = Callable[[], tuple[MutableInMemoryFactBase, RuleBase]]


def _seed_data_linear() -> tuple[MutableInMemoryFactBase, RuleBase]:
    x = Variable("X")
    y = Variable("Y")
    u = Variable("U")

    a = Constant("a")
    p = Predicate("p", 2)
    guard = Predicate("guard", 1)

    facts = MutableInMemoryFactBase(
        [
            Atom(p, a, x),
            Atom(p, x, x),
            Atom(p, x, y),
            Atom(p, a, y),
            Atom(guard, a),
        ]
    )
    rules = RuleBase({Rule(Atom(guard, u), Atom(guard, u), "guard_reflexive")})
    return facts, rules


def _seed_data_nonlinear() -> tuple[MutableInMemoryFactBase, RuleBase]:
    x = Variable("X")
    y = Variable("Y")
    z = Variable("Z")
    u = Variable("U")

    a = Constant("a")
    b = Constant("b")
    c = Constant("c")

    p = Predicate("p", 2)
    guard = Predicate("guard", 1)

    facts = MutableInMemoryFactBase(
        [
            Atom(p, a, x),
            Atom(p, y, x),
            Atom(p, y, z),
            Atom(p, a, u),
            Atom(p, b, u),
            Atom(p, c, c),
            Atom(guard, a),
        ]
    )
    rules = RuleBase({Rule(Atom(guard, u), Atom(guard, u), "guard_reflexive")})
    return facts, rules


_CASES: tuple[tuple[str, CaseBuilder], ...] = (
    ("linear", _seed_data_linear),
    ("nonlinear", _seed_data_nonlinear),
)


def _expected_core(case_builder: CaseBuilder) -> MutableInMemoryFactBase:
    fact_base, rule_base = case_builder()
    chase = test_builder(fact_base, rule_base).build().get()
    chase.execute()
    expected = MutableInMemoryFactBase(fact_base)
    MutableMaterializedCoreProcessor(NaiveCoreProcessor()).compute_core(expected)
    return expected


class TestComputeLocalCorePort(unittest.TestCase):
    def test_compute_local_core_treatment_keeps_core_and_equivalence(self) -> None:
        expected_map = {
            case_name: _expected_core(builder) for case_name, builder in _CASES
        }

        for processor_name, processor_factory in _PROCESSOR_FACTORIES:
            for case_name, case_builder in _CASES:
                expected = expected_map[case_name]
                for applier_name, configure in _APPLIERS:
                    with self.subTest(
                        processor=processor_name,
                        case=case_name,
                        applier=applier_name,
                    ):
                        fact_base, rule_base = case_builder()
                        treatment = ComputeLocalCore(
                            MutableMaterializedCoreProcessor(processor_factory())
                        )
                        chase = (
                            configure(test_builder(fact_base, rule_base))
                            .add_step_end_treatments(treatment)
                            .build()
                            .get()
                        )
                        chase.execute()

                        self.assertTrue(is_core(fact_base))
                        self.assertTrue(is_equivalent(fact_base, expected))


if __name__ == "__main__":
    unittest.main()
