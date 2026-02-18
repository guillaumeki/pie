"""Debug treatment printing chase step details."""

from __future__ import annotations

import time

from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.treatment.end_treatment import (
    EndTreatment,
)


class Debug(EndTreatment):
    def __init__(self) -> None:
        self._chase: Chase | None = None
        self._time_ms = int(time.time() * 1000)

    def init(self, chase: Chase) -> None:
        self._chase = chase
        self._time_ms = int(time.time() * 1000)

    def apply(self) -> None:
        if self._chase is None:
            return
        now = int(time.time() * 1000)
        result = self._chase.get_last_step_results()
        created_count = (
            len(result.created_facts) if result.created_facts is not None else 0
        )
        print("---")
        print(f"Step: {self._chase.get_step_count()}")
        print(
            "Atoms:",
            len(self._chase.get_chasable_data().get_writing_target()),
        )
        print(f"Added atoms: {created_count}")
        print(f"Time: {now - self._time_ms}")
        print(f"Last step rules: {len(result.applied_rules or ())}")
        self._time_ms = now
