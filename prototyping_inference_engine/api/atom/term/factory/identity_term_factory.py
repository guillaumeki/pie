"""
Factories for identity-based term instances.
"""

from typing import Set, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.storage.storage_strategy import (
        TermStorageStrategy,
    )


class IdentityVariableFactory:
    def __init__(self, storage: "TermStorageStrategy[str, object]") -> None:
        self._storage = storage
        self._fresh_counter = 0

    def create(self, identifier: str):
        from prototyping_inference_engine.api.atom.term.identity_variable import (
            IdentityVariable,
        )

        return self._storage.get_or_create(
            identifier, lambda: IdentityVariable(identifier)
        )

    def fresh(self):
        identifier = f"_FV{self._fresh_counter}"
        while self._storage.contains(identifier):
            self._fresh_counter += 1
            identifier = f"_FV{self._fresh_counter}"
        self._fresh_counter += 1
        return self.create(identifier)

    @property
    def tracked(self) -> Set[object]:
        return self._storage.tracked_items()

    def __len__(self) -> int:
        return len(self._storage)


class IdentityConstantFactory:
    def __init__(self, storage: "TermStorageStrategy[object, object]") -> None:
        self._storage = storage

    def create(self, identifier: object):
        from prototyping_inference_engine.api.atom.term.identity_constant import (
            IdentityConstant,
        )

        return self._storage.get_or_create(
            identifier, lambda: IdentityConstant(identifier)
        )

    @property
    def tracked(self) -> Set[object]:
        return self._storage.tracked_items()

    def __len__(self) -> int:
        return len(self._storage)


class IdentityLiteralFactory:
    def __init__(self, storage: "TermStorageStrategy[object, object]") -> None:
        self._storage = storage

    def create(
        self, lexical: str, datatype: str | None = None, lang: str | None = None
    ):
        from prototyping_inference_engine.api.atom.term.identity_literal import (
            IdentityLiteral,
        )

        key = (lexical, datatype, lang)
        return self._storage.get_or_create(
            key, lambda: IdentityLiteral(lexical, datatype, lexical, lang, key)
        )

    @property
    def tracked(self) -> Set[object]:
        return self._storage.tracked_items()

    def __len__(self) -> int:
        return len(self._storage)
