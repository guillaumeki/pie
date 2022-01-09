from api.atom.frozen_atom_set import FrozenAtomSet
from api.fact_base.in_memory_fact_base import InMemoryFactBase


class FrozenInMemoryFactBase(InMemoryFactBase):
    def __init__(self):
        InMemoryFactBase.__init__(FrozenAtomSet())

    @property
    def atom_set(self) -> FrozenAtomSet:
        return self._atom_set
