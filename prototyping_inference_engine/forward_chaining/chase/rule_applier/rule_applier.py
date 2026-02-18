"""Apply a set of rules for one chase step."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.rule_application_step_result import (
    RuleApplicationStepResult,
)


class RuleApplier(ABC):
    @abstractmethod
    def init(self, chase: Chase) -> None: ...

    @abstractmethod
    def apply(
        self,
        rules: Collection[Rule],
        chasable_data: ChasableData,
    ) -> RuleApplicationStepResult: ...

    def describe(self) -> str:
        return self.__class__.__name__

    def describe_json(self) -> str:
        return f'{{"class": "{self.describe()}"}}'
