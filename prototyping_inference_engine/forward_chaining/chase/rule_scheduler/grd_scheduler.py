"""Rule scheduler based on GRD dependencies."""

from __future__ import annotations

from collections.abc import Collection

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.rule_scheduler import (
    RuleScheduler,
)


class GRDScheduler(RuleScheduler):
    def __init__(self, rule_base: RuleBase | None = None) -> None:
        self._rule_base: RuleBase | None = None
        self._grd: GRD | None = None
        if rule_base is not None:
            self.init(rule_base)

    def init(self, rule_base: RuleBase) -> None:
        self._rule_base = rule_base
        self._grd = GRD(rule_base.rules)

    def get_rules_to_apply(
        self,
        last_applied_rules: Collection[Rule] | None,
    ) -> Collection[Rule]:
        if self._rule_base is None:
            return []
        if last_applied_rules is None:
            return set(self._rule_base.rules)
        if self._grd is None:
            return set()

        triggered: set[Rule] = set()
        for rule in last_applied_rules:
            triggered.update(self._grd.get_triggered_rules(rule))
        return triggered
