from typing import Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.set.index.index_by_predicate import (
    IndexByPredicate,
)


@runtime_checkable
class IndexedByPredicateAtomSet(Protocol):
    """Protocol for atom sets that provide an index by predicate."""

    @property
    def index_by_predicate(self) -> IndexByPredicate: ...
