"""Stop when atom count reaches limit."""

from __future__ import annotations

from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)


class LimitAtoms(HaltingCondition):
    def __init__(self, max_atoms: int):
        self._max_atoms = max_atoms
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def check(self) -> bool:
        if self._chase is None:
            return False
        return (
            len(self._chase.get_chasable_data().get_writing_target()) < self._max_atoms
        )
