"""Fact-base abstractions and implementations."""

from prototyping_inference_engine.api.fact_base.fact_base import (
    FactBase,
    UnsupportedFactBaseOperation,
)
from prototyping_inference_engine.api.fact_base.factory import FactBaseFactory
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)

__all__ = [
    "FactBase",
    "UnsupportedFactBaseOperation",
    "FactBaseFactory",
    "FrozenInMemoryFactBase",
    "MutableInMemoryFactBase",
]
