"""Builder to create configurable chase algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.forward_chaining.chase.chase_impl import ChaseImpl
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data_impl import (
    ChasableDataImpl,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.created_facts_at_previous_step import (
    CreatedFactsAtPreviousStep,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.halting_condition import (
    HaltingCondition,
)
from prototyping_inference_engine.forward_chaining.chase.halting_condition.has_rules_to_apply import (
    HasRulesToApply,
)
from prototyping_inference_engine.forward_chaining.chase.metachase.stratified.stratified_chase_builder import (
    StratifiedChaseBuilder,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.breadth_first_trigger_rule_applier import (
    BreadthFirstTriggerRuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.multi_thread_rule_applier import (
    MultiThreadRuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.parallel_trigger_rule_applier import (
    ParallelTriggerRuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.rule_applier import (
    RuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.source_delegated_datalog_rule_applier import (
    SourceDelegatedDatalogRuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.body_to_query_transformer.all_transformer import (
    AllTransformer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.body_to_query_transformer.body_to_query_transformer import (
    BodyToQueryTransformer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.body_to_query_transformer.frontier_transformer import (
    FrontierTransformer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.facts_handler.delegated_application import (
    DelegatedApplication,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.facts_handler.direct_application import (
    DirectApplication,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.facts_handler.facts_handler import (
    FactsHandler,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.body_skolem import (
    BodyPseudoSkolem,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.fresh_renamer import (
    FreshRenamer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.frontier_by_piece_skolem import (
    FrontierByPiecePseudoSkolem,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.frontier_skolem import (
    FrontierPseudoSkolem,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.frontier_by_piece_true_skolem import (
    FrontierByPieceTrueSkolem,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.frontier_true_skolem import (
    FrontierTrueSkolem,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.body_true_skolem import (
    BodyTrueSkolem,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.trigger_renamer import (
    TriggerRenamer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.trigger_applier import (
    TriggerApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.trigger_applier_impl import (
    TriggerApplierImpl,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.always_true_checker import (
    AlwaysTrueChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.equivalent_checker import (
    EquivalentChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.multi_trigger_checker import (
    MultiTriggerChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.oblivious_checker import (
    ObliviousChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.restricted_checker import (
    RestrictedChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.semi_oblivious_checker import (
    SemiObliviousChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.trigger_checker import (
    TriggerChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.naive_trigger_computer import (
    NaiveTriggerComputer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.restricted_trigger_computer import (
    RestrictedTriggerComputer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.semi_naive_computer import (
    SemiNaiveComputer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.trigger_computer import (
    TriggerComputer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.two_steps_computer import (
    TwoStepsComputer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.by_predicate_scheduler import (
    ByPredicateScheduler,
)
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.grd_scheduler import (
    GRDScheduler,
)
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.naive_scheduler import (
    NaiveScheduler,
)
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.rule_scheduler import (
    RuleScheduler,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.add_created_facts import (
    AddCreatedFacts,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.debug import Debug
from prototyping_inference_engine.forward_chaining.chase.treatment.end_treatment import (
    EndTreatment,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.pretreatment import (
    Pretreatment,
)


@dataclass
class _BuildOptional:
    value: ChaseImpl | None

    def get(self) -> ChaseImpl:
        if self.value is None:
            raise RuntimeError("Builder is not fully configured")
        return self.value

    def or_else_none(self) -> ChaseImpl | None:
        return self.value


class ChaseBuilder:
    def __init__(self) -> None:
        self._hcs: list[HaltingCondition] = []
        self._global_pts: list[Pretreatment] = []
        self._step_pts: list[Pretreatment] = []
        self._global_end_ts: list[EndTreatment] = []
        self._end_step_ts: list[EndTreatment] = []

        self._chasable_data: ChasableData | None = None
        self._rb: RuleBase | None = None
        self._rsc: RuleScheduler | None = None
        self._ra: RuleApplier | None = None
        self._transf: BodyToQueryTransformer | None = None
        self._tc: TriggerComputer | None = None
        self._tch: TriggerChecker | None = None
        self._ta: TriggerApplier | None = None
        self._fh: FactsHandler | None = None
        self._tn: TriggerRenamer | None = None

        self._scheduler: Literal["grd", "naive", "by_predicate"] = "grd"
        self._applier: Literal[
            "parallel",
            "breadth_first",
            "multi_thread_parallel",
            "source_delegated_datalog",
        ] = "parallel"
        self._transformer: Literal["frontier", "all"] = "frontier"
        self._computer: Literal["naive", "semi_naive", "two_step", "restricted"] = (
            "naive"
        )
        self._checker: Literal[
            "semi_oblivious",
            "oblivious",
            "restricted",
            "equivalent",
            "true",
            "so_restricted",
        ] = "semi_oblivious"
        self._application: Literal["parallel", "direct"] = "parallel"
        self._skolem: Literal[
            "fresh",
            "pseudo_body",
            "pseudo_frontier",
            "pseudo_frontier_piece",
            "true_body",
            "true_frontier",
            "true_frontier_piece",
        ] = "fresh"
        self._debug = False

    @staticmethod
    def default_builder(chasable_data_or_fb, rb: RuleBase) -> "ChaseBuilder":
        if isinstance(chasable_data_or_fb, ChasableData):
            chasable_data = chasable_data_or_fb
        else:
            chasable_data = ChasableDataImpl(chasable_data_or_fb)
        return ChaseBuilder().set_chasable_data(chasable_data).set_rule_base(rb)

    @staticmethod
    def default_chase(chasable_data_or_fb, rb: RuleBase):
        return ChaseBuilder.default_builder(chasable_data_or_fb, rb).build().get()

    def build(self) -> _BuildOptional:
        if self._minimal_config() is None:
            return _BuildOptional(None)
        assert self._chasable_data is not None
        assert self._rb is not None
        assert self._rsc is not None
        assert self._ra is not None
        return _BuildOptional(
            ChaseImpl(
                self._chasable_data,
                self._rb,
                self._rsc,
                self._ra,
                self._hcs,
                self._global_pts,
                self._step_pts,
                self._global_end_ts,
                self._end_step_ts,
            )
        )

    def _minimal_config(self) -> "ChaseBuilder" | None:
        if self._chasable_data is None or self._rb is None:
            return None

        if self._rsc is None:
            if self._scheduler == "naive":
                self._rsc = NaiveScheduler(self._rb)
            elif self._scheduler == "by_predicate":
                self._rsc = ByPredicateScheduler(self._rb)
            else:
                self._rsc = GRDScheduler(self._rb)

        if self._ra is None:
            if self._applier in {"parallel", "breadth_first", "multi_thread_parallel"}:
                if self._transf is None:
                    self._transf = (
                        AllTransformer()
                        if self._transformer == "all"
                        else FrontierTransformer()
                    )
                if self._tc is None:
                    if self._computer == "semi_naive":
                        self._tc = SemiNaiveComputer()
                    elif self._computer == "two_step":
                        self._tc = TwoStepsComputer()
                    elif self._computer == "restricted":
                        self._tc = RestrictedTriggerComputer()
                    else:
                        self._tc = NaiveTriggerComputer()
                if self._tch is None:
                    if self._checker == "true":
                        self._tch = AlwaysTrueChecker()
                    elif self._checker == "oblivious":
                        self._tch = ObliviousChecker()
                    elif self._checker == "restricted":
                        self._tch = RestrictedChecker()
                    elif self._checker == "equivalent":
                        self._tch = EquivalentChecker()
                    elif self._checker == "so_restricted":
                        self._tch = MultiTriggerChecker(
                            [SemiObliviousChecker(), RestrictedChecker()]
                        )
                    else:
                        self._tch = SemiObliviousChecker()

                if self._ta is None:
                    if self._tn is None:
                        if self._skolem == "pseudo_body":
                            self._tn = BodyPseudoSkolem()
                        elif self._skolem == "pseudo_frontier":
                            self._tn = FrontierPseudoSkolem()
                        elif self._skolem == "pseudo_frontier_piece":
                            self._tn = FrontierByPiecePseudoSkolem()
                        elif self._skolem == "true_body":
                            self._tn = BodyTrueSkolem()
                        elif self._skolem == "true_frontier":
                            self._tn = FrontierTrueSkolem()
                        elif self._skolem == "true_frontier_piece":
                            self._tn = FrontierByPieceTrueSkolem()
                        else:
                            self._tn = FreshRenamer()
                    if self._fh is None:
                        self._fh = (
                            DirectApplication()
                            if self._application == "direct"
                            else DelegatedApplication()
                        )
                    self._ta = TriggerApplierImpl(self._tn, self._fh)

            assert self._transf is not None
            assert self._tc is not None
            assert self._tch is not None
            assert self._ta is not None
            if self._applier == "breadth_first":
                self._ra = BreadthFirstTriggerRuleApplier(
                    self._transf, self._tc, self._tch, self._ta
                )
            elif self._applier == "multi_thread_parallel":
                self._ra = MultiThreadRuleApplier(
                    self._transf, self._tc, self._tch, self._ta
                )
            elif self._applier == "source_delegated_datalog":
                self._ra = SourceDelegatedDatalogRuleApplier()
            else:
                self._ra = ParallelTriggerRuleApplier(
                    self._transf, self._tc, self._tch, self._ta
                )

        if not self._hcs:
            self.add_standard_halting_conditions()

        if self._application == "parallel":
            self._end_step_ts.insert(0, AddCreatedFacts())

        if self._debug:
            self.add_step_end_treatments(Debug())

        return self

    def use_trigger_rule_applier(self) -> "ChaseBuilder":
        self._applier = "breadth_first"
        return self

    def use_naive_rule_scheduler(self) -> "ChaseBuilder":
        self._scheduler = "naive"
        return self

    def use_grd_rule_scheduler(self) -> "ChaseBuilder":
        self._scheduler = "grd"
        return self

    def use_by_predicate_rule_scheduler(self) -> "ChaseBuilder":
        self._scheduler = "by_predicate"
        return self

    def use_all_transformer(self) -> "ChaseBuilder":
        self._transformer = "all"
        return self

    def use_frontier_transformer(self) -> "ChaseBuilder":
        self._transformer = "frontier"
        return self

    def use_naive_computer(self) -> "ChaseBuilder":
        self._computer = "naive"
        return self

    def use_restricted_computer(self) -> "ChaseBuilder":
        self._computer = "restricted"
        return self

    def use_semi_naive_computer(self) -> "ChaseBuilder":
        self._computer = "semi_naive"
        return self

    def use_two_step_computer(self) -> "ChaseBuilder":
        self._computer = "two_step"
        return self

    def use_source_delegated_datalog_application(self) -> "ChaseBuilder":
        self._applier = "source_delegated_datalog"
        return self

    def use_always_true_checker(self) -> "ChaseBuilder":
        self._checker = "true"
        return self

    def use_oblivious_checker(self) -> "ChaseBuilder":
        self._checker = "oblivious"
        return self

    def use_semi_oblivious_checker(self) -> "ChaseBuilder":
        self._checker = "semi_oblivious"
        return self

    def use_restricted_checker(self) -> "ChaseBuilder":
        self._checker = "restricted"
        return self

    def use_equivalent_checker(self) -> "ChaseBuilder":
        self._checker = "equivalent"
        return self

    def use_so_restricted_checker(self) -> "ChaseBuilder":
        self._checker = "so_restricted"
        return self

    def use_fresh_naming(self) -> "ChaseBuilder":
        self._skolem = "fresh"
        return self

    def use_body_skolem(self) -> "ChaseBuilder":
        self._skolem = "pseudo_body"
        return self

    def use_frontier_skolem(self) -> "ChaseBuilder":
        self._skolem = "pseudo_frontier"
        return self

    def use_frontier_by_piece_skolem(self) -> "ChaseBuilder":
        self._skolem = "pseudo_frontier_piece"
        return self

    def use_body_pseudo_skolem(self) -> "ChaseBuilder":
        self._skolem = "pseudo_body"
        return self

    def use_frontier_pseudo_skolem(self) -> "ChaseBuilder":
        self._skolem = "pseudo_frontier"
        return self

    def use_frontier_by_piece_pseudo_skolem(self) -> "ChaseBuilder":
        self._skolem = "pseudo_frontier_piece"
        return self

    def use_body_true_skolem(self) -> "ChaseBuilder":
        self._skolem = "true_body"
        return self

    def use_frontier_true_skolem(self) -> "ChaseBuilder":
        self._skolem = "true_frontier"
        return self

    def use_frontier_by_piece_true_skolem(self) -> "ChaseBuilder":
        self._skolem = "true_frontier_piece"
        return self

    def set_chasable_data(self, chasable_data: ChasableData) -> "ChaseBuilder":
        self._chasable_data = chasable_data
        return self

    def set_rule_base(self, rb: RuleBase) -> "ChaseBuilder":
        self._rb = rb
        return self

    def set_rule_scheduler(self, scheduler: RuleScheduler) -> "ChaseBuilder":
        self._rsc = scheduler
        return self

    def set_rule_applier(self, rule_applier: RuleApplier) -> "ChaseBuilder":
        self._ra = rule_applier
        return self

    def set_body_to_query_transformer(
        self, transformer: BodyToQueryTransformer
    ) -> "ChaseBuilder":
        self._transf = transformer
        return self

    def set_trigger_computer(self, computer: TriggerComputer) -> "ChaseBuilder":
        self._tc = computer
        return self

    def set_trigger_checker(self, checker: TriggerChecker) -> "ChaseBuilder":
        self._tch = checker
        return self

    def set_trigger_applier(self, applier: TriggerApplier) -> "ChaseBuilder":
        self._ta = applier
        return self

    def set_existentials_renamer(self, renamer: TriggerRenamer) -> "ChaseBuilder":
        self._tn = renamer
        return self

    def set_new_facts_handler(self, facts_handler: FactsHandler) -> "ChaseBuilder":
        self._fh = facts_handler
        return self

    def add_standard_halting_conditions(self) -> "ChaseBuilder":
        self.add_halting_conditions(CreatedFactsAtPreviousStep(), HasRulesToApply())
        return self

    def add_halting_conditions(self, *conditions: HaltingCondition) -> "ChaseBuilder":
        self._hcs.extend(conditions)
        return self

    def add_global_pretreatments(self, *pretreatments: Pretreatment) -> "ChaseBuilder":
        self._global_pts.extend(pretreatments)
        return self

    def add_step_pretreatments(self, *pretreatments: Pretreatment) -> "ChaseBuilder":
        self._step_pts.extend(pretreatments)
        return self

    def add_global_end_treatments(
        self, *end_treatments: EndTreatment
    ) -> "ChaseBuilder":
        self._global_end_ts.extend(end_treatments)
        return self

    def add_step_end_treatments(self, *end_treatments: EndTreatment) -> "ChaseBuilder":
        self._end_step_ts.extend(end_treatments)
        return self

    def debug(self) -> "ChaseBuilder":
        self._debug = True
        return self

    def use_breadth_first_applier(self) -> "ChaseBuilder":
        self._application = "direct"
        self._applier = "breadth_first"
        return self

    def use_parallel_applier(self) -> "ChaseBuilder":
        self._application = "parallel"
        self._applier = "parallel"
        return self

    def use_multi_thread_rule_applier(self) -> "ChaseBuilder":
        self._application = "parallel"
        self._applier = "multi_thread_parallel"
        return self

    def use_source_delegated_datalog_applier(self) -> "ChaseBuilder":
        self._applier = "source_delegated_datalog"
        return self

    def use_stratified_chase(self) -> StratifiedChaseBuilder:
        builder = StratifiedChaseBuilder(self)
        if self._chasable_data is not None:
            builder.set_chasable_data(self._chasable_data)
        if self._rb is not None:
            builder.set_rule_base(self._rb)
        return builder
