from abc import abstractmethod

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.index.IndexedAtomSet import IndexedAtomSet
from prototyping_inference_engine.api.atom.set.index.index import Index
from prototyping_inference_engine.api.atom.set.index.index_by_predicate import IndexByPredicate


class IndexedByPredicateAtomSet(IndexedAtomSet):
    @property
    @abstractmethod
    def index_by_predicate(self) -> IndexByPredicate:
        pass

    @property
    def index(self) -> Index:
        return self.index_by_predicate
