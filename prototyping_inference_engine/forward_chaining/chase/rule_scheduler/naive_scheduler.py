"""Naive scheduler returning all rules at every step."""

from __future__ import annotations

from collections.abc import Collection

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.rule_scheduler import (
    RuleScheduler,
)


class NaiveScheduler(RuleScheduler):
    def __init__(self, rule_base: RuleBase | None = None) -> None:
        self._rule_base: RuleBase | None = None
        if rule_base is not None:
            self.init(rule_base)

    def init(self, rule_base: RuleBase) -> None:
        self._rule_base = rule_base

    def get_rules_to_apply(
        self,
        last_applied_rules: Collection[Rule] | None,
    ) -> Collection[Rule]:
        if self._rule_base is None:
            return []
        return set(self._rule_base.rules)
