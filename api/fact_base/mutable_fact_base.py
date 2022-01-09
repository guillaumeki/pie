from abc import abstractmethod
from typing import Iterable

from api.atom.atom import Atom
from api.fact_base.fact_base import FactBase, fact_base_operation


class MutableFactBase(FactBase):
    @abstractmethod
    @fact_base_operation
    def add(self, atom: Atom):
        pass

    @fact_base_operation
    def update(self, atoms: Iterable[Atom]):
        for atom in atoms:
            self.add(atom)
