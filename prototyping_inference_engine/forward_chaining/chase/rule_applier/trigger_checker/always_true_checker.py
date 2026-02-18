"""Checker accepting all triggers."""

from __future__ import annotations

from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.trigger_checker import (
    TriggerChecker,
)


class AlwaysTrueChecker(TriggerChecker):
    def check(
        self,
        rule: Rule,
        substitution: Substitution,
        read_write_data: FactBase,
    ) -> bool:
        return True
