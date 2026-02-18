"""Halting condition abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prototyping_inference_engine.forward_chaining.chase.chase import Chase


class HaltingCondition(ABC):
    """Check if chase can continue."""

    @abstractmethod
    def init(self, chase: Chase) -> None: ...

    @abstractmethod
    def check(self) -> bool: ...

    def describe(self) -> str:
        return self.__class__.__name__
