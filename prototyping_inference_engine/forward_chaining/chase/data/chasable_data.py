"""Abstraction for chasable data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.fact_base.fact_base import FactBase


class ChasableData(ABC):
    """Data wrapper containing writing target and read-only sources."""

    @abstractmethod
    def get_writing_target(self) -> FactBase: ...

    @abstractmethod
    def get_data_sources(self) -> tuple[ReadableData, ...]: ...

    @abstractmethod
    def get_all_readable_data(self) -> ReadableData: ...

    @abstractmethod
    def set_data_sources(self, sources: Iterable[ReadableData]) -> None: ...
