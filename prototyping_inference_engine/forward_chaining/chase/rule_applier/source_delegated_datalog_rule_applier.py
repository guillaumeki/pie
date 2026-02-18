"""Source-delegated datalog rule applier with fallback."""

from __future__ import annotations

from collections.abc import Collection

from prototyping_inference_engine.api.data.datalog_delegable import DatalogDelegable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.rule_application_step_result import (
    RuleApplicationStepResult,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.breadth_first_trigger_rule_applier import (
    BreadthFirstTriggerRuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.rule_applier import (
    RuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.body_to_query_transformer.all_transformer import (
    AllTransformer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.facts_handler.direct_application import (
    DirectApplication,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.fresh_renamer import (
    FreshRenamer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.trigger_applier_impl import (
    TriggerApplierImpl,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.oblivious_checker import (
    ObliviousChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.naive_trigger_computer import (
    NaiveTriggerComputer,
)


class SourceDelegatedDatalogRuleApplier(RuleApplier):
    def __init__(self, fallback: RuleApplier | None = None):
        self._fallback = fallback or BreadthFirstTriggerRuleApplier(
            AllTransformer(),
            NaiveTriggerComputer(),
            ObliviousChecker(),
            TriggerApplierImpl(FreshRenamer(), DirectApplication()),
        )

    def init(self, chase: Chase) -> None:
        self._fallback.init(chase)

    def apply(
        self,
        rules: Collection[Rule],
        chasable_data: ChasableData,
    ) -> RuleApplicationStepResult:
        target = chasable_data.get_writing_target()
        sources = chasable_data.get_data_sources()

        if isinstance(target, DatalogDelegable) and not sources:
            datalog_rules = {rule for rule in rules if not rule.existential_variables}
            existential_rules = {rule for rule in rules if rule.existential_variables}

            changed = target.delegate_rules(datalog_rules) if datalog_rules else False
            existential_result = self._fallback.apply(existential_rules, chasable_data)
            applied = set(existential_result.applied_rules or set()) | datalog_rules

            if existential_result.created_facts is None:
                if changed:
                    return RuleApplicationStepResult(frozenset(applied), None)
                return RuleApplicationStepResult.from_created(applied, [])

            return RuleApplicationStepResult(
                frozenset(applied),
                existential_result.created_facts,
            )

        return self._fallback.apply(rules, chasable_data)

    def describe(self) -> str:
        return f"{self.__class__.__name__} with fallback {self._fallback.describe()}"

    def describe_json(self) -> str:
        return (
            "{\n"
            f'  "class": "{self.__class__.__name__}",\n'
            f'  "fallback": "{self._fallback.describe()}"\n'
            "}"
        )
