"""Stratified chase meta-algorithm."""

from __future__ import annotations

from collections.abc import Collection

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.description.stratified_chase_description import (
    StratifiedChaseDescription,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)
from prototyping_inference_engine.forward_chaining.chase.rule_application_step_result import (
    RuleApplicationStepResult,
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


class StratifiedChase(Chase):
    def __init__(
        self,
        builder,
        chasable_data: ChasableData,
        strata: list[RuleBase],
        halting_conditions: Collection[HaltingCondition],
        global_pretreatments: Collection[Pretreatment],
        step_pretreatments: Collection[Pretreatment],
        global_end_treatments: Collection[EndTreatment],
        end_of_step_treatments: Collection[EndTreatment],
    ) -> None:
        self._chasable_data = chasable_data
        self._strata = list(strata)
        self._chase_builder = builder
        self._chase_builder.set_chasable_data(chasable_data)

        self._halting_conditions = tuple(halting_conditions)
        self._global_pretreatments = tuple(global_pretreatments)
        self._step_pretreatments = tuple(step_pretreatments)
        self._global_end_treatments = tuple(global_end_treatments)
        self._end_of_step_treatments = tuple(end_of_step_treatments)

        self._chase: Chase | None = None
        self._step_number = 0

    def has_next_step(self) -> bool:
        return self._step_number < len(self._strata) and all(
            condition.check() for condition in self._halting_conditions
        )

    def next_step(self) -> None:
        chase = (
            self._chase_builder.set_rule_base(self._strata[self._step_number])
            .build()
            .or_else_none()
        )
        if chase is None:
            raise RuntimeError("The chase builder cannot build a chase instance.")
        self._chase = chase
        chase.execute()
        self._step_number += 1

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

    def get_chasable_data(self) -> ChasableData:
        return self._chasable_data

    def get_rule_base(self) -> RuleBase:
        return self._strata[self._step_number]

    def set_rule_base(self, rule_base: RuleBase) -> None:
        raise NotImplementedError(
            "Setting a new rule base is unsupported for StratifiedChase."
        )

    def get_last_step_results(self) -> RuleApplicationStepResult:
        if self._chase is None:
            return RuleApplicationStepResult.initial()
        return self._chase.get_last_step_results()

    def get_rule_scheduler(self) -> RuleScheduler:
        if self._chase is None:
            raise RuntimeError("No internal chase has run yet.")
        return self._chase.get_rule_scheduler()

    def get_step_count(self) -> int:
        return self._step_number

    def describe(self) -> str:
        return self.get_description().to_pretty_string()

    def get_description(self) -> StratifiedChaseDescription:
        return StratifiedChaseDescription(
            chasable_data=self._chasable_data,
            strata=self._strata,
            chase=self._chase,
            chase_builder=self._chase_builder,
            halting_conditions=self._halting_conditions,
            global_pretreatments=self._global_pretreatments,
            step_pretreatments=self._step_pretreatments,
            global_end_treatments=self._global_end_treatments,
            end_of_step_treatments=self._end_of_step_treatments,
            step_number=self._step_number,
        )

    def _init_all(self) -> None:
        self._init_treatments(self._global_pretreatments)
        self._init_treatments(self._step_pretreatments)
        self._init_treatments(self._end_of_step_treatments)
        self._init_treatments(self._global_end_treatments)
        for condition in self._halting_conditions:
            condition.init(self)

    def _init_treatments(self, treatments: Collection[Treatment]) -> None:
        for treatment in treatments:
            treatment.init(self)
