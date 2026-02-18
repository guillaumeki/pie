"""Treatment adding created facts to writing target."""

from __future__ import annotations

from typing import cast

from prototyping_inference_engine.api.fact_base.protocols import Writable
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.treatment.end_treatment import (
    EndTreatment,
)


class AddCreatedFacts(EndTreatment):
    def __init__(self) -> None:
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def apply(self) -> None:
        if self._chase is None:
            return
        created = self._chase.get_last_step_results().created_facts
        if created is None:
            return
        target = cast(Writable, self._chase.get_chasable_data().get_writing_target())
        for atom in created:
            target.add(atom)
