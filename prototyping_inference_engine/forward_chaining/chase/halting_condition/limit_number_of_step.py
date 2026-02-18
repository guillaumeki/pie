"""Stop when a step limit is reached."""

from __future__ import annotations

from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)


class LimitNumberOfStep(HaltingCondition):
    def __init__(self, max_steps: int):
        self._max_steps = max_steps
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def check(self) -> bool:
        if self._chase is None:
            return False
        return self._chase.get_step_count() < self._max_steps
