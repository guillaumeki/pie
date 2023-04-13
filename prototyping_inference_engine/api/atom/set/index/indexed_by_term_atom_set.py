from abc import abstractmethod

from prototyping_inference_engine.api.atom.set.index.IndexedAtomSet import IndexedAtomSet
from prototyping_inference_engine.api.atom.set.index.index import Index
from prototyping_inference_engine.api.atom.set.index.index_by_term import IndexByTerm


class IndexedByTermAtomSet(IndexedAtomSet):
    @property
    @abstractmethod
    def index_by_term(self) -> IndexByTerm:
        pass

    @property
    def index(self) -> Index:
        return self.index_by_term
