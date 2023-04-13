from abc import ABC, abstractmethod

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.substitution.substitution import Substitution


class BacktrackScheduler(ABC):
    def __init__(self, from_atom_set: AtomSet):
        self._atom_set_from = from_atom_set

    @abstractmethod
    def has_next_atom(self, level: int) -> bool:
        pass

    @abstractmethod
    def next_atom(self, sub: Substitution, level: int) -> Atom:
        pass
