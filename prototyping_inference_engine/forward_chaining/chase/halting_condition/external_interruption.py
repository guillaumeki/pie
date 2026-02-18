"""Stop on external interruption flag."""

from __future__ import annotations

from threading import Event

from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)


class ExternalInterruption(HaltingCondition):
    def __init__(self, stop_event: Event):
        self._stop_event = stop_event

    def init(self, chase: Chase) -> None:
        return None

    def check(self) -> bool:
        # Continue while not interrupted.
        return not self._stop_event.is_set()
