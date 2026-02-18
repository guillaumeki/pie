"""Transform a rule body into an FOQuery."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery


class BodyToQueryTransformer(ABC):
    @abstractmethod
    def transform(self, rule: Rule) -> FOQuery: ...

    def describe(self) -> str:
        return self.__class__.__name__
