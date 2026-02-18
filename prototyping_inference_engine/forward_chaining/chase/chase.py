"""Chase interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.forward_chaining.api.forward_chaining_algorithm import (
    ForwardChainingAlgorithm,
)
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.rule_scheduler.rule_scheduler import (
    RuleScheduler,
)
from prototyping_inference_engine.forward_chaining.chase.rule_application_step_result import (
    RuleApplicationStepResult,
)


class Chase(ForwardChainingAlgorithm, ABC):
    """A chase saturates chasable data according to a rule base."""

    @abstractmethod
    def has_next_step(self) -> bool: ...

    @abstractmethod
    def next_step(self) -> None: ...

    @abstractmethod
    def apply_global_pretreatments(self) -> None: ...

    @abstractmethod
    def apply_pretreatments(self) -> None: ...

    @abstractmethod
    def apply_end_of_step_treatments(self) -> None: ...

    @abstractmethod
    def apply_global_end_treatments(self) -> None: ...

    @abstractmethod
    def get_rule_base(self) -> RuleBase: ...

    @abstractmethod
    def set_rule_base(self, rule_base: RuleBase) -> None: ...

    @abstractmethod
    def get_last_step_results(self) -> RuleApplicationStepResult: ...

    @abstractmethod
    def get_step_count(self) -> int: ...

    @abstractmethod
    def get_chasable_data(self) -> ChasableData: ...

    @abstractmethod
    def get_rule_scheduler(self) -> RuleScheduler: ...

    def execute(self) -> None:
        self.apply_global_pretreatments()
        while self.has_next_step():
            self.apply_pretreatments()
            self.next_step()
            self.apply_end_of_step_treatments()
        self.apply_global_end_treatments()
