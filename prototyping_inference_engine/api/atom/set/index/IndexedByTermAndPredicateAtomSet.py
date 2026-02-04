from typing import Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.set.index.index_by_term_and_predicate import (
    IndexByTermAndPredicate,
)


@runtime_checkable
class IndexedByTermAndPredicateAtomSet(Protocol):
    """Protocol for atom sets that provide an index by term and predicate."""

    @property
    def index_by_term_and_predicate(self) -> IndexByTermAndPredicate: ...
