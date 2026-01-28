from typing import Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.set.index.index import Index


@runtime_checkable
class IndexedAtomSet(Protocol):
    """Protocol for atom sets that provide an index."""

    @property
    def index(self) -> Index:
        ...
