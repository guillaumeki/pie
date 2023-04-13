from abc import abstractmethod

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.index.index import Index


class IndexedAtomSet(AtomSet):
    @property
    @abstractmethod
    def index(self) -> Index:
        pass
