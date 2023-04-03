from abc import ABC, abstractmethod
from typing import Iterator

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.substitution.substitution import Substitution


class HomomorphismAlgorithm(ABC):
    @abstractmethod
    def compute_homomorphisms(self, from_atom_set: AtomSet,
                              to_atom_set: AtomSet,
                              sub: Substitution = None) -> Iterator[Substitution]:
        pass

    def exist_homomorphism(self,
                           from_atom_set:
                           AtomSet, to_atom_set: AtomSet,
                           sub: Substitution = None) -> bool:
        try:
            next(iter(self.compute_homomorphisms(from_atom_set, to_atom_set, sub)))
        except StopIteration:
            return False

        return True
