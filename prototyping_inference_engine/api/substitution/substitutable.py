from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

class Substitutable(Generic[T], ABC):
    @abstractmethod
    def apply_substitution(self, substitution) -> T:
        pass