"""Result object for one chase step."""

from __future__ import annotations

from dataclasses import dataclass

from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.ontology.rule.rule import Rule


@dataclass(frozen=True)
class RuleApplicationStepResult:
    """Result of a chase step: applied rules and created facts."""

    applied_rules: frozenset[Rule] | None
    created_facts: FactBase | None

    @staticmethod
    def initial() -> "RuleApplicationStepResult":
        return RuleApplicationStepResult(None, None)

    @staticmethod
    def from_created(
        applied_rules: set[Rule],
        created_atoms,
    ) -> "RuleApplicationStepResult":
        if created_atoms is None:
            return RuleApplicationStepResult(frozenset(applied_rules), None)
        return RuleApplicationStepResult(
            frozenset(applied_rules),
            MutableInMemoryFactBase(created_atoms),
        )

    def describe(self) -> str:
        if self.created_facts is None or self.applied_rules is None:
            return "No rule applied yet."
        return (
            f"Applied {len(self.applied_rules)} rules in the last step; "
            f"inferred {len(self.created_facts)} atoms."
        )
