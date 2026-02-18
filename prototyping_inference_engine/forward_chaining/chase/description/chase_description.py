"""Description object for chase configuration and status."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Collection

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.rule_application_step_result import (
    RuleApplicationStepResult,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.rule_applier import (
    RuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.rule_scheduler import (
    RuleScheduler,
)


@dataclass(frozen=True)
class ChaseDescription:
    chasable_data: ChasableData
    rule_base: RuleBase
    rule_scheduler: RuleScheduler
    rule_applier: RuleApplier
    last_step_result: RuleApplicationStepResult
    step_number: int
    halting_conditions: Collection
    global_pretreatments: Collection
    step_pretreatments: Collection
    global_end_treatments: Collection
    end_of_step_treatments: Collection

    def to_json(self) -> str:
        def to_names(values: Collection) -> list[str]:
            return [str(value) for value in values]

        return (
            "{\n"
            f'  "writingTargetSize": {len(self.chasable_data.get_writing_target())},\n'
            f'  "ruleBaseSize": {len(self.rule_base.rules)},\n'
            f'  "ruleScheduler": "{self.rule_scheduler.describe()}",\n'
            f'  "ruleApplier": "{self.rule_applier.describe_json()}",\n'
            f'  "lastStepResult": "{self.last_step_result.describe()}",\n'
            f'  "stepNumber": {self.step_number},\n'
            f'  "haltingConditions": {to_names(self.halting_conditions)},\n'
            f'  "globalPretreatments": {to_names(self.global_pretreatments)},\n'
            f'  "stepPretreatments": {to_names(self.step_pretreatments)},\n'
            f'  "globalEndTreatments": {to_names(self.global_end_treatments)},\n'
            f'  "endOfStepTreatments": {to_names(self.end_of_step_treatments)}\n'
            "}"
        )

    def to_pretty_string(self) -> str:
        lines = [
            "ChaseImpl",
            f"|-- WritingTarget (size): {len(self.chasable_data.get_writing_target())}",
            f"|-- RuleBase (size): {len(self.rule_base.rules)}",
            f"|-- RuleScheduler: {self.rule_scheduler.describe()}",
            f"|-- RuleApplier: {self.rule_applier.describe()}",
            f"|-- LastStepResult: {self.last_step_result.describe()}",
            f"|-- StepNumber: {self.step_number}",
            f"|-- HaltingConditions: {[str(v) for v in self.halting_conditions]}",
            f"|-- GlobalPretreatments: {[str(v) for v in self.global_pretreatments]}",
            f"|-- StepPretreatments: {[str(v) for v in self.step_pretreatments]}",
            f"|-- GlobalEndTreatments: {[str(v) for v in self.global_end_treatments]}",
            f"`-- EndOfStepTreatments: {[str(v) for v in self.end_of_step_treatments]}",
        ]
        return "\n".join(lines)
