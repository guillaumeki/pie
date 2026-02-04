from abc import ABC, abstractmethod
from typing import Optional, TypeVar

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.term.variable import Variable

AS = TypeVar("AS", bound=AtomSet)


class CoreAlgorithm(ABC):
    """
    This (abstract) class represents an algorithm that computes the core of a set of atoms
    A core of a set of atoms is the set without its redundancies
    """

    @abstractmethod
    def compute_core(
        self, atom_set: AS, freeze: Optional[tuple[Variable, ...]] = None
    ) -> AS:
        """
        Compute and return the core of a set of atoms
        @param atom_set: the set of atoms from which the redundancies should be removed
        @param freeze: the variables in the set of atoms that will be treated as constants
        @return: the core of atom_set
        """
        pass
