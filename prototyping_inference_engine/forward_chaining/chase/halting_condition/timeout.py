"""Stop when elapsed time exceeds timeout."""

from __future__ import annotations

import time

from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)


class Timeout(HaltingCondition):
    def __init__(self, timeout_ms: int):
        self._timeout_ns = timeout_ms * 1_000_000
        self._start_ns = 0

    def init(self, chase: Chase) -> None:
        self._start_ns = time.perf_counter_ns()

    def check(self) -> bool:
        return (time.perf_counter_ns() - self._start_ns) < self._timeout_ns
