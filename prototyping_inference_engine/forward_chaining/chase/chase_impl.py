"""Default chase implementation."""

from __future__ import annotations

from collections.abc import Collection

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.description.chase_description import (
    ChaseDescription,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
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
from prototyping_inference_engine.forward_chaining.chase.treatment.end_treatment import (
    EndTreatment,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.pretreatment import (
    Pretreatment,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.treatment import (
    Treatment,
)


class ChaseImpl(Chase):
    def __init__(
        self,
        chasable_data: ChasableData,
        rb: RuleBase,
        rule_scheduler: RuleScheduler,
        rule_applier: RuleApplier,
        halting_conditions: Collection[HaltingCondition],
        global_pretreatments: Collection[Pretreatment],
        step_pretreatments: Collection[Pretreatment],
        global_end_treatments: Collection[EndTreatment],
        end_of_step_treatments: Collection[EndTreatment],
    ) -> None:
        self._chasable_data = chasable_data
        self._rb = rb
        self._rule_scheduler = rule_scheduler
        self._rule_applier = rule_applier
        self._halting_conditions = tuple(halting_conditions)
        self._global_pretreatments = tuple(global_pretreatments)
        self._step_pretreatments = tuple(step_pretreatments)
        self._global_end_treatments = tuple(global_end_treatments)
        self._end_of_step_treatments = tuple(end_of_step_treatments)

        self._last_step_result = RuleApplicationStepResult.initial()
        self._step_number = 0

    def has_next_step(self) -> bool:
        return all(condition.check() for condition in self._halting_conditions)

    def next_step(self) -> None:
        self._step_number += 1
        rules_to_apply = self._rule_scheduler.get_rules_to_apply(
            self._last_step_result.applied_rules
        )
        self._last_step_result = self._rule_applier.apply(
            rules_to_apply,
            self._chasable_data,
        )

    def apply_global_pretreatments(self) -> None:
        self._init_all()
        for treatment in self._global_pretreatments:
            treatment.apply()

    def apply_pretreatments(self) -> None:
        for treatment in self._step_pretreatments:
            treatment.apply()

    def apply_end_of_step_treatments(self) -> None:
        for treatment in self._end_of_step_treatments:
            treatment.apply()

    def apply_global_end_treatments(self) -> None:
        for treatment in self._global_end_treatments:
            treatment.apply()

    def get_rule_base(self) -> RuleBase:
        return self._rb

    def set_rule_base(self, rule_base: RuleBase) -> None:
        if self._step_number > 0:
            raise RuntimeError(
                "The rule base should not be changed after the chase is run. "
                "Create a new chase object instead."
            )
        self._rb = rule_base
        self._rule_scheduler.init(rule_base)
        self._last_step_result = RuleApplicationStepResult.initial()

    def get_last_step_results(self) -> RuleApplicationStepResult:
        return self._last_step_result

    def get_step_count(self) -> int:
        return self._step_number

    def get_chasable_data(self) -> ChasableData:
        return self._chasable_data

    def get_rule_scheduler(self) -> RuleScheduler:
        return self._rule_scheduler

    def get_description(self) -> ChaseDescription:
        return ChaseDescription(
            chasable_data=self._chasable_data,
            rule_base=self._rb,
            rule_scheduler=self._rule_scheduler,
            rule_applier=self._rule_applier,
            last_step_result=self._last_step_result,
            step_number=self._step_number,
            halting_conditions=self._halting_conditions,
            global_pretreatments=self._global_pretreatments,
            step_pretreatments=self._step_pretreatments,
            global_end_treatments=self._global_end_treatments,
            end_of_step_treatments=self._end_of_step_treatments,
        )

    def describe(self) -> str:
        return self.get_description().to_pretty_string()

    def _init_all(self) -> None:
        self._init_treatments(self._global_pretreatments)
        self._init_treatments(self._step_pretreatments)
        self._rule_applier.init(self)
        self._rule_scheduler.init(self._rb)
        self._init_treatments(self._end_of_step_treatments)
        self._init_treatments(self._global_end_treatments)
        for condition in self._halting_conditions:
            condition.init(self)

    def _init_treatments(self, treatments: Collection[Treatment]) -> None:
        for treatment in treatments:
            treatment.init(self)
