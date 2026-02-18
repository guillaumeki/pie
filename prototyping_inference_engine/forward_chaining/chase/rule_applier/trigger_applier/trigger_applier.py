"""Apply a trigger substitution to a rule head."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TriggerApplier(ABC):
    @abstractmethod
    def apply(
        self,
        rule: Rule,
        substitution: Substitution,
        read_write_data: FactBase,
    ) -> Formula | None: ...

    def describe(self) -> str:
        return self.__class__.__name__
