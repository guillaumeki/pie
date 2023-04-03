from abc import ABC, abstractmethod
from typing import TypeVar

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.term.variable import Variable

AS = TypeVar("AS", bound=AtomSet)


class CoreAlgorithm(ABC):
    @abstractmethod
    def compute_core(self, atom_set: AS, freeze: tuple[Variable] = None) -> AS:
        pass
