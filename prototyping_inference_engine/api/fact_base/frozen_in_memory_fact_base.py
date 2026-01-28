from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.fact_base.in_memory_fact_base import InMemoryFactBase


class FrozenInMemoryFactBase(InMemoryFactBase):
    def __init__(self, atoms: Iterable[Atom] = None):
        super().__init__(FrozenAtomSet(atoms))
