from typing import Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.set.index.index_by_term import IndexByTerm


@runtime_checkable
class IndexedByTermAtomSet(Protocol):
    """Protocol for atom sets that provide an index by term."""

    @property
    def index_by_term(self) -> IndexByTerm:
        ...
