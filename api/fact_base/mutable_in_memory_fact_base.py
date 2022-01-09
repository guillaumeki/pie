from typing import List, Tuple, Iterable

from api.atom.atom import Atom
from api.atom.mutable_atom_set import MutableAtomSet
from api.atom.term.term import Term
from api.fact_base.in_memory_fact_base import InMemoryFactBase
from api.fact_base.mutable_fact_base import MutableFactBase
from api.query.query import Query


class MutableInMemoryFactBase(InMemoryFactBase, MutableFactBase):
    def __init__(self):
        InMemoryFactBase.__init__(MutableAtomSet())

    def add(self, atom: Atom):
        self.atom_set.add(atom)

    @property
    def atom_set(self) -> MutableAtomSet:
        return self._atom_set  # type: ignore
