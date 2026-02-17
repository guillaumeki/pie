"""Writable collection for heterogeneous readable sources."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, TYPE_CHECKING, cast

from prototyping_inference_engine.api.data.collection.protocols import Queryable
from prototyping_inference_engine.api.data.collection.readable_collection import (
    ReadableDataCollection,
)
from prototyping_inference_engine.api.fact_base.protocols import Writable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.predicate import Predicate


class WritableReadableDataCollection(ReadableDataCollection, Writable):
    """Readable collection that routes writes to writable sources."""

    def __init__(
        self,
        sources: Dict["Predicate", Queryable],
        dynamic_sources: Optional[List[Queryable]] = None,
        default_writable: Optional[Writable] = None,
    ):
        super().__init__(sources=sources, dynamic_sources=dynamic_sources)
        self._default_writable = default_writable
        if default_writable is not None and default_writable not in self._all_sources:
            self._all_sources.append(cast(Queryable, default_writable))

    def _writable_for(self, predicate: "Predicate") -> Optional[Writable]:
        source = self._get_source(predicate)
        if isinstance(source, Writable):
            return source
        return self._default_writable

    def add(self, atom: "Atom") -> None:
        writable = self._writable_for(atom.predicate)
        if writable is None:
            raise KeyError(f"No writable source for predicate {atom.predicate}")
        writable.add(atom)
        if atom.predicate not in self._sources:
            self._sources[atom.predicate] = cast(Queryable, writable)

    def update(self, atoms: Iterable["Atom"]) -> None:
        for atom in atoms:
            self.add(atom)

    def remove(self, atom: "Atom") -> None:
        writable = self._writable_for(atom.predicate)
        if writable is None:
            raise KeyError(f"No writable source for predicate {atom.predicate}")
        writable.remove(atom)

    def remove_all(self, atoms: Iterable["Atom"]) -> None:
        for atom in atoms:
            self.remove(atom)
