from abc import ABC, abstractmethod

from prototyping_inference_engine.api.atom.set.index.index import Index
from prototyping_inference_engine.api.atom.set.index.index_by_predicate import IndexByPredicate
from prototyping_inference_engine.api.atom.set.index.index_by_term import IndexByTerm
from prototyping_inference_engine.api.atom.set.index.index_by_term_and_predicate import IndexByTermAndPredicate
from prototyping_inference_engine.api.atom.set.index.indexed_by_predicate_atom_set import IndexedByPredicateAtomSet
from prototyping_inference_engine.api.atom.set.index.indexed_by_term_atom_set import IndexedByTermAtomSet


class IndexedByTermAndPredicateAtomSet(IndexedByTermAtomSet, IndexedByPredicateAtomSet, ABC):
    @property
    @abstractmethod
    def index_by_term_and_predicate(self) -> IndexByTermAndPredicate:
        pass

    @property
    def index_by_predicate(self) -> IndexByPredicate:
        return self.index_by_term_and_predicate

    @property
    def index_by_term(self) -> IndexByTerm:
        return self.index_by_term_and_predicate

    @property
    def index(self) -> Index:
        return self.index_by_term_and_predicate
