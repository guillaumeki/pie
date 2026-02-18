"""Rule scheduler abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.rule.rule import Rule


class RuleScheduler(ABC):
    """Compute rules to apply at next step from last applied rules."""

    @abstractmethod
    def init(self, rule_base: RuleBase) -> None: ...

    @abstractmethod
    def get_rules_to_apply(
        self,
        last_applied_rules: Collection[Rule] | None,
    ) -> Collection[Rule]: ...

    def describe(self) -> str:
        return self.__class__.__name__
