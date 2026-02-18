"""Composite trigger checker."""

from __future__ import annotations

from collections.abc import Iterable

from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.trigger_checker import (
    TriggerChecker,
)


class MultiTriggerChecker(TriggerChecker):
    def __init__(self, checkers: Iterable[TriggerChecker]):
        self._checkers = tuple(checkers)

    def check(
        self,
        rule: Rule,
        substitution: Substitution,
        read_write_data: FactBase,
    ) -> bool:
        return all(
            checker.check(rule, substitution, read_write_data)
            for checker in self._checkers
        )
