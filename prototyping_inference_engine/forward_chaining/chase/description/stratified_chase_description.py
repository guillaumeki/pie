"""Description object for stratified chase configuration and status."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Collection

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)


@dataclass(frozen=True)
class StratifiedChaseDescription:
    chasable_data: ChasableData
    strata: list[RuleBase]
    chase: object
    chase_builder: object
    halting_conditions: Collection
    global_pretreatments: Collection
    step_pretreatments: Collection
    global_end_treatments: Collection
    end_of_step_treatments: Collection
    step_number: int

    def to_json(self) -> str:
        strata_json = [
            {"stratumIndex": i, "ruleCount": len(stratum.rules)}
            for i, stratum in enumerate(self.strata)
        ]
        return (
            "{\n"
            f'  "writingTargetSize": {len(self.chasable_data.get_writing_target())},\n'
            f'  "strata": {strata_json},\n'
            f'  "currentStepNumber": {self.step_number}\n'
            "}"
        )

    def to_pretty_string(self) -> str:
        return (
            "StratifiedChase\n"
            f"|-- WritingTarget (size): {len(self.chasable_data.get_writing_target())}\n"
            f"|-- Strata: {[len(stratum.rules) for stratum in self.strata]}\n"
            f"`-- Current Step Number: {self.step_number}"
        )
