"""Treatment abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prototyping_inference_engine.forward_chaining.chase.chase import Chase


class Treatment(ABC):
    @abstractmethod
    def init(self, chase: Chase) -> None: ...

    @abstractmethod
    def apply(self) -> None: ...

    def describe(self) -> str:
        return self.__class__.__name__
