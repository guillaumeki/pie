"""Forward chaining algorithm abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ForwardChainingAlgorithm(ABC):
    """A forward-chaining algorithm saturating data with rules."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the algorithm until halting conditions stop it."""
