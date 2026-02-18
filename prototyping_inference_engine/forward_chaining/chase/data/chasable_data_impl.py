"""Default chasable data implementation."""

from __future__ import annotations

from typing import Iterable

from prototyping_inference_engine.api.data.collection.builder import (
    ReadableCollectionBuilder,
)
from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)


class ChasableDataImpl(ChasableData):
    """Default holder for a writable fact base and optional side sources."""

    def __init__(
        self,
        writing_target: FactBase,
        data_sources: Iterable[ReadableData] = (),
    ) -> None:
        self._writing_target = writing_target
        self._data_sources = tuple(data_sources)

    def get_writing_target(self) -> FactBase:
        return self._writing_target

    def get_data_sources(self) -> tuple[ReadableData, ...]:
        return self._data_sources

    def set_data_sources(self, sources: Iterable[ReadableData]) -> None:
        self._data_sources = tuple(sources)

    def get_all_readable_data(self) -> ReadableData:
        builder = ReadableCollectionBuilder().add_all_predicates_from(
            self._writing_target
        )
        for source in self._data_sources:
            builder.add_all_predicates_from(source)
        return builder.build()
