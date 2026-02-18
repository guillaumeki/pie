"""Builder for stratified chase."""

from __future__ import annotations

from collections import defaultdict

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.limit_number_of_step import (
    LimitNumberOfStep,
)
from prototyping_inference_engine.forward_chaining.chase.metachase.stratified.stratified_chase import (
    StratifiedChase,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.debug import Debug
from prototyping_inference_engine.forward_chaining.chase.treatment.end_treatment import (
    EndTreatment,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.predicate_filter_end_treatment import (
    PredicateFilterEndTreatment,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.pretreatment import (
    Pretreatment,
)
from prototyping_inference_engine.grd.grd import GRD
from prototyping_inference_engine.grd.stratification import (
    BySccStratification,
    MinimalStratification,
    SingleEvaluationStratification,
)


class _BuildOptional:
    def __init__(self, value):
        self._value = value

    def get(self):
        if self._value is None:
            raise RuntimeError("Builder is not fully configured")
        return self._value

    def or_else_none(self):
        return self._value


class StratifiedChaseBuilder:
    def __init__(self, chase_builder=None) -> None:
        self._halting_conditions: list[HaltingCondition] = []
        self._global_pretreatments: list[Pretreatment] = []
        self._step_pretreatments: list[Pretreatment] = []
        self._global_end_treatments: list[EndTreatment] = []
        self._end_of_step_treatments: list[EndTreatment] = []
        self._predicates_to_remove_by_step: dict[int, set[Predicate]] = defaultdict(set)

        self._chase_builder = chase_builder
        self._chasable_data: ChasableData | None = None
        self._rule_base: RuleBase | None = None
        self._strata: list[RuleBase] = []

        self._debug = False
        self._stratification_method = "none"
        self._final_predicates: list[Predicate] | None = None

    @staticmethod
    def default_builder(
        chasable_data: ChasableData, rb: RuleBase
    ) -> "StratifiedChaseBuilder":
        from prototyping_inference_engine.forward_chaining.chase.chase_builder import (
            ChaseBuilder,
        )

        return (
            StratifiedChaseBuilder(ChaseBuilder())
            .set_chasable_data(chasable_data)
            .set_rule_base(rb)
        )

    def set_chase_builder(self, chase_builder) -> "StratifiedChaseBuilder":
        self._chase_builder = chase_builder
        return self

    def set_chasable_data(
        self, chasable_data: ChasableData
    ) -> "StratifiedChaseBuilder":
        self._chasable_data = chasable_data
        return self

    def set_rule_base(self, rb: RuleBase) -> "StratifiedChaseBuilder":
        self._rule_base = rb
        return self

    def set_strata(self, strata: list[RuleBase]) -> "StratifiedChaseBuilder":
        self._strata = list(strata)
        self._stratification_method = "none"
        return self

    def use_pseudo_minimal_stratification(self) -> "StratifiedChaseBuilder":
        self._stratification_method = "pseudo_minimal"
        return self

    def use_stratification(self) -> "StratifiedChaseBuilder":
        self._stratification_method = "default"
        return self

    def use_single_evaluation_stratification(self) -> "StratifiedChaseBuilder":
        self._stratification_method = "single_evaluation"
        return self

    def add_halting_conditions(
        self, *conditions: HaltingCondition
    ) -> "StratifiedChaseBuilder":
        self._halting_conditions.extend(conditions)
        return self

    def add_global_pretreatments(
        self, *treatments: Pretreatment
    ) -> "StratifiedChaseBuilder":
        self._global_pretreatments.extend(treatments)
        return self

    def add_step_pretreatments(
        self, *treatments: Pretreatment
    ) -> "StratifiedChaseBuilder":
        self._step_pretreatments.extend(treatments)
        return self

    def add_global_end_treatments(
        self, *treatments: EndTreatment
    ) -> "StratifiedChaseBuilder":
        self._global_end_treatments.extend(treatments)
        return self

    def add_end_of_step_treatments(
        self, *treatments: EndTreatment
    ) -> "StratifiedChaseBuilder":
        self._end_of_step_treatments.extend(treatments)
        return self

    def set_final_predicates(
        self, predicates: list[Predicate]
    ) -> "StratifiedChaseBuilder":
        self._final_predicates = list(predicates)
        return self

    def debug(self) -> "StratifiedChaseBuilder":
        self._debug = True
        return self

    def build(self) -> _BuildOptional:
        if self._chase_builder is None:
            from prototyping_inference_engine.forward_chaining.chase.chase_builder import (
                ChaseBuilder,
            )

            self._chase_builder = ChaseBuilder()

        if self._chasable_data is None:
            return _BuildOptional(None)
        if self._rule_base is None and not self._strata:
            return _BuildOptional(None)

        self._chase_builder.set_chasable_data(self._chasable_data)

        if not self._strata:
            if self._rule_base is None:
                return _BuildOptional(None)
            grd = GRD(self._rule_base.rules)
            if self._stratification_method == "pseudo_minimal":
                computed = grd.stratify(MinimalStratification())
                if computed is None:
                    raise ValueError("The rule base must be stratifiable")
                self._strata = computed
            elif self._stratification_method == "default":
                self._strata = grd.stratify(BySccStratification()) or []
            elif self._stratification_method == "single_evaluation":
                computed = grd.stratify(SingleEvaluationStratification())
                if computed is None:
                    raise ValueError("The rule base must be stratifiable")
                self._strata = computed
                self._chase_builder.add_halting_conditions(LimitNumberOfStep(1))
            else:
                self._strata = [self._rule_base]

        if self._final_predicates is not None:
            self._calculate_predicates_to_remove()
            self.add_end_of_step_treatments(
                PredicateFilterEndTreatment(self._predicates_to_remove_by_step)
            )

        if self._debug:
            self.add_end_of_step_treatments(Debug())

        return _BuildOptional(
            StratifiedChase(
                self._chase_builder,
                self._chasable_data,
                self._strata,
                self._halting_conditions,
                self._global_pretreatments,
                self._step_pretreatments,
                self._global_end_treatments,
                self._end_of_step_treatments,
            )
        )

    def _calculate_predicates_to_remove(self) -> None:
        if self._final_predicates is None:
            return

        body_preds_by_stratum: list[set[Predicate]] = []
        for rule_base in self._strata:
            body_preds: set[Predicate] = set()
            for rule in rule_base.rules:
                body_preds.update(atom.predicate for atom in rule.body.atoms)
            body_preds_by_stratum.append(body_preds)

        required_by_stratum: list[set[Predicate]] = [set() for _ in self._strata]
        acc = set(self._final_predicates)
        for idx in range(len(self._strata) - 1, -1, -1):
            required_by_stratum[idx] = set(acc)
            acc.update(body_preds_by_stratum[idx])

        produced: set[Predicate] = set()
        for idx, stratum in enumerate(self._strata):
            for rule in stratum.rules:
                produced.update(atom.predicate for atom in rule.head.atoms)
            self._predicates_to_remove_by_step[idx + 1] = {
                predicate
                for predicate in produced
                if predicate not in required_by_stratum[idx]
            }
