"""
Created on 23 déc. 2021

@author: guillaume
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.substitution.substitutable import Substitutable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class Term(Substitutable["Term"], ABC):
    def __init__(self, identifier: object):
        self._identifier = identifier

    @property
    def identifier(self) -> object:
        return self._identifier

    @property
    @abstractmethod
    def is_ground(self) -> bool:
        """True if this term is ground (contains no variables)."""
        pass

    @property
    @abstractmethod
    def comparison_priority(self) -> int:
        """Priority for representative selection (lower = higher priority)."""
        pass

    @abstractmethod
    def apply_substitution(self, substitution: "Substitution") -> "Term":
        pass

    def __str__(self):
        return str(self.identifier)
