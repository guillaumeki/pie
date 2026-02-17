"""Core processor adapter for mutable materialized data sources."""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.variable import Variable


@runtime_checkable
class MutableMaterializedData(Protocol):
    """Minimal mutable materialized-data surface required for core processing."""

    def __iter__(self): ...

    def add(self, atom: Atom) -> None: ...

    def remove(self, atom: Atom) -> None: ...

    def remove_all(self, atoms) -> None: ...


class MutableMaterializedCoreProcessor:
    """Apply a CoreAlgorithm on mutable materialized stores in-place."""

    def __init__(self, algorithm: CoreAlgorithm) -> None:
        self._algorithm = algorithm

    def compute_core(
        self,
        data: MutableMaterializedData,
        freeze: Optional[tuple[Variable, ...]] = None,
    ) -> None:
        freeze = tuple() if freeze is None else freeze
        source = FrozenAtomSet(data)
        core = self._algorithm.compute_core(source, freeze)

        source_atoms = set(source)
        core_atoms = set(core)
        data.remove_all(source_atoms - core_atoms)
