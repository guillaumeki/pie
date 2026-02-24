"""Ported compute-core treatment tests for forward chaining."""

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
from prototyping_inference_engine.forward_chaining.chase.treatment.compute_core import (
    ComputeCore,
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


def _seed_data() -> tuple[MutableInMemoryFactBase, RuleBase]:
    x = Variable("X")
    y = Variable("Y")
    u = Variable("U")

    a = Constant("a")
    b = Constant("b")
    z = Constant("z")

    r = Predicate("r", 1)
    t = Predicate("t", 3)
    s = Predicate("s", 2)
    related_to = Predicate("relatedTo", 2)
    guard = Predicate("guard", 1)

    facts = MutableInMemoryFactBase(
        [
            Atom(r, x),
            Atom(t, x, a, b),
            Atom(s, a, z),
            Atom(r, y),
            Atom(t, y, a, b),
            Atom(related_to, y, z),
            Atom(guard, a),
        ]
    )
    rules = RuleBase({Rule(Atom(guard, u), Atom(guard, u), "guard_reflexive")})
    return facts, rules


def _expected_core() -> MutableInMemoryFactBase:
    fact_base, rule_base = _seed_data()
    chase = test_builder(fact_base, rule_base).build().get()
    chase.execute()
    expected = MutableInMemoryFactBase(fact_base)
    MutableMaterializedCoreProcessor(NaiveCoreProcessor()).compute_core(expected)
    return expected


class TestComputeCorePort(unittest.TestCase):
    def test_compute_core_treatment_keeps_core_and_equivalence(self) -> None:
        expected = _expected_core()

        for processor_name, processor_factory in _PROCESSOR_FACTORIES:
            for applier_name, configure in _APPLIERS:
                with self.subTest(processor=processor_name, applier=applier_name):
                    fact_base, rule_base = _seed_data()
                    treatment = ComputeCore(
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
