"""Handle created facts before they are returned as step output."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.formula.formula import Formula


class FactsHandler(ABC):
    @abstractmethod
    def add(self, new_facts: Formula, read_write_data: FactBase) -> Formula | None: ...
