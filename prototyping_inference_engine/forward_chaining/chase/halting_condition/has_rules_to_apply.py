"""Stop when scheduler has no rule to apply."""

from __future__ import annotations

from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)


class HasRulesToApply(HaltingCondition):
    def __init__(self) -> None:
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def check(self) -> bool:
        if self._chase is None:
            return False
        rules = self._chase.get_rule_scheduler().get_rules_to_apply(
            self._chase.get_last_step_results().applied_rules
        )
        return len(rules) > 0
