"""Compute trigger substitutions for a shared rule body."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)


class TriggerComputer(ABC):
    @abstractmethod
    def init(self, chase: Chase) -> None: ...

    @abstractmethod
    def compute(
        self,
        body: FOQuery,
        rules: Collection[Rule],
        chasable_data: ChasableData,
    ) -> Iterable[Substitution]: ...

    def describe(self) -> str:
        return self.__class__.__name__
