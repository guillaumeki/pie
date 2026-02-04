from typing import Iterable, Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.fact_base.in_memory_fact_base import (
    InMemoryFactBase,
)


class MutableInMemoryFactBase(InMemoryFactBase):
    def __init__(self, atoms: Optional[Iterable[Atom]] = None):
        storage = MutableAtomSet(atoms)
        super().__init__(storage)
        self._storage: MutableAtomSet = storage

    # Writable
    def add(self, atom: Atom) -> None:
        self._storage.add(atom)

    def update(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.add(atom)
