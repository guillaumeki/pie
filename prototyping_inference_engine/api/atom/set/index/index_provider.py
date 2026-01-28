from typing import Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.index.index import Index


@runtime_checkable
class IndexProvider(Protocol):
    """Protocol for providing an Index from an AtomSet."""

    def get_index(self, atom_set: AtomSet) -> Index:
        ...


class IndexByTermProvider:
    """Provides IndexByTerm, reusing existing index if available."""

    def get_index(self, atom_set: AtomSet) -> Index:
        from prototyping_inference_engine.api.atom.set.index.index_by_term import IndexByTerm
        from prototyping_inference_engine.api.atom.set.index.indexed_by_term_atom_set import IndexedByTermAtomSet

        if isinstance(atom_set, IndexedByTermAtomSet):
            return atom_set.index_by_term
        return IndexByTerm(atom_set)


class IndexByPredicateProvider:
    """Provides IndexByPredicate, reusing existing index if available."""

    def get_index(self, atom_set: AtomSet) -> Index:
        from prototyping_inference_engine.api.atom.set.index.index_by_predicate import IndexByPredicate
        from prototyping_inference_engine.api.atom.set.index.indexed_by_predicate_atom_set import IndexedByPredicateAtomSet

        if isinstance(atom_set, IndexedByPredicateAtomSet):
            return atom_set.index_by_predicate
        return IndexByPredicate(atom_set)


class IndexByTermAndPredicateProvider:
    """Provides IndexByTermAndPredicate, reusing existing index if available."""

    def get_index(self, atom_set: AtomSet) -> Index:
        from prototyping_inference_engine.api.atom.set.index.index_by_term_and_predicate import IndexByTermAndPredicate
        from prototyping_inference_engine.api.atom.set.index.IndexedByTermAndPredicateAtomSet import IndexedByTermAndPredicateAtomSet

        if isinstance(atom_set, IndexedByTermAndPredicateAtomSet):
            return atom_set.index_by_term_and_predicate
        return IndexByTermAndPredicate(atom_set)


class BestAvailableIndexProvider:
    """Provides the best available index from an AtomSet."""

    def get_index(self, atom_set: AtomSet) -> Index:
        from prototyping_inference_engine.api.atom.set.index.index_by_term_and_predicate import IndexByTermAndPredicate
        from prototyping_inference_engine.api.atom.set.index.IndexedAtomSet import IndexedAtomSet

        if isinstance(atom_set, IndexedAtomSet):
            return atom_set.index
        return IndexByTermAndPredicate(atom_set)
