"""Stop when no new facts were inferred at previous step."""

from __future__ import annotations

from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)


class CreatedFactsAtPreviousStep(HaltingCondition):
    def __init__(self) -> None:
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def check(self) -> bool:
        if self._chase is None:
            return False
        created = self._chase.get_last_step_results().created_facts
        if created is None:
            return True
        return len(created) > 0
