"""End treatment removing atoms by predicate per step."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.fact_base.protocols import Writable
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.treatment.end_treatment import (
    EndTreatment,
)


class PredicateFilterEndTreatment(EndTreatment):
    def __init__(
        self,
        predicates_to_remove_by_step: Mapping[int, set[Predicate]],
    ):
        self._predicates_to_remove_by_step = dict(predicates_to_remove_by_step)
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def apply(self) -> None:
        if self._chase is None:
            return
        current_step = self._chase.get_step_count()
        to_remove = self._predicates_to_remove_by_step.get(current_step, set())
        if not to_remove:
            return

        target = cast(Writable, self._chase.get_chasable_data().get_writing_target())
        for predicate in to_remove:
            atoms = list(
                self._chase.get_chasable_data()
                .get_writing_target()
                .get_atoms_by_predicate(predicate)
            )
            if atoms:
                target.remove_all(atoms)
