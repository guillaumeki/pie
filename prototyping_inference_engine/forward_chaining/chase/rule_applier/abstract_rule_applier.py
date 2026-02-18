"""Base implementation for rule appliers using trigger pipeline."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Collection

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.rule_applier.body_to_query_transformer.body_to_query_transformer import (
    BodyToQueryTransformer,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.rule_applier import (
    RuleApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.trigger_applier import (
    TriggerApplier,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_checker.trigger_checker import (
    TriggerChecker,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.trigger_computer import (
    TriggerComputer,
)


class AbstractRuleApplier(RuleApplier):
    def __init__(
        self,
        transformer: BodyToQueryTransformer,
        computer: TriggerComputer,
        checker: TriggerChecker,
        applier: TriggerApplier,
    ) -> None:
        self.transformer = transformer
        self.computer = computer
        self.checker = checker
        self.applier = applier

    def init(self, chase: Chase) -> None:
        self.computer.init(chase)

    def group_rules_by_body_query(
        self,
        rules: Collection[Rule],
    ) -> dict[FOQuery, list[Rule]]:
        grouped: dict[FOQuery, list[Rule]] = defaultdict(list)
        for rule in rules:
            grouped[self.transformer.transform(rule)].append(rule)
        return grouped

    def describe(self) -> str:
        return (
            "\n"
            f"|-- TriggerComputer: {self.computer.describe()}\n"
            f"|-- TriggerChecker: {self.checker.describe()}\n"
            f"|-- TriggerApplier: {self.applier.describe()}\n"
            f"`-- BodyToQueryTransformer: {self.transformer.describe()}"
        )

    def describe_json(self) -> str:
        return (
            "{\n"
            f'  "TriggerComputer": "{self.computer.describe()}",\n'
            f'  "TriggerChecker": "{self.checker.describe()}",\n'
            f'  "TriggerApplier": "{self.applier.describe()}",\n'
            f'  "BodyToQueryTransformer": "{self.transformer.describe()}"\n'
            "}"
        )
