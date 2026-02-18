"""Oblivious checker: same rule+substitution only once."""

from __future__ import annotations

from collections import defaultdict

from prototyping_inference_engine.forward_chaining.chase.rule_applier.substitution_key import (
    substitution_key,
)

from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.trigger_checker import (
    TriggerChecker,
)


class ObliviousChecker(TriggerChecker):
    def __init__(self) -> None:
        self._already_treated: dict[Rule, set[tuple[tuple[object, object], ...]]] = (
            defaultdict(set)
        )

    def check(
        self,
        rule: Rule,
        substitution: Substitution,
        read_write_data: FactBase,
    ) -> bool:
        treated = self._already_treated[rule]
        key = substitution_key(substitution)
        if key in treated:
            return False
        treated.add(key)
        return True
