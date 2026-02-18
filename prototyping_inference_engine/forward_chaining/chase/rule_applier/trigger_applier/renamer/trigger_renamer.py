"""Renaming strategy for existential variables."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TriggerRenamer(ABC):
    @abstractmethod
    def rename_existentials(
        self, rule: Rule, substitution: Substitution
    ) -> Substitution: ...
