"""Treatment computing core on writing target."""

from __future__ import annotations

from typing import cast

from prototyping_inference_engine.api.fact_base.core.fact_base_core_processor import (
    MutableMaterializedData,
    MutableMaterializedCoreProcessor,
)
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.treatment.end_treatment import (
    EndTreatment,
)
from prototyping_inference_engine.forward_chaining.chase.treatment.pretreatment import (
    Pretreatment,
)


class ComputeCore(Pretreatment, EndTreatment):
    def __init__(self, processor: MutableMaterializedCoreProcessor):
        self._processor = processor
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def apply(self) -> None:
        if self._chase is None:
            return
        writing_target = self._chase.get_chasable_data().get_writing_target()
        self._processor.compute_core(cast(MutableMaterializedData, writing_target))
