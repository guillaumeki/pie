"""
Factory for identity-based predicates.
"""

from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.storage.storage_strategy import (
        TermStorageStrategy,
    )


class IdentityPredicateFactory:
    def __init__(self, storage: "TermStorageStrategy[tuple[str, int], object]") -> None:
        self._storage = storage

    def create(self, name: str, arity: int):
        from prototyping_inference_engine.api.atom.identity_predicate import (
            IdentityPredicate,
        )

        key = (name, arity)
        return self._storage.get_or_create(key, lambda: IdentityPredicate(name, arity))

    @property
    def tracked(self) -> Set[object]:
        return self._storage.tracked_items()

    def __len__(self) -> int:
        return len(self._storage)
