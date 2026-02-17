"""Protocols used by storage backends."""

from typing import Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.data.storage.acceptance import AcceptanceResult


@runtime_checkable
class AtomAcceptance(Protocol):
    """Writable storages can expose explicit acceptance constraints."""

    def accepts_predicate(self, predicate: Predicate) -> AcceptanceResult: ...

    def accepts_atom(self, atom: Atom) -> AcceptanceResult: ...
