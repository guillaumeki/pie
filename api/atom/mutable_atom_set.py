"""
Created on 26 déc. 2021

@author: guillaume
"""
from collections.abc import MutableSet
from typing import Iterable

from api.atom.atom import Atom
from api.atom.atom_set import AtomSet


class MutableAtomSet(AtomSet, MutableSet):
    def __init__(self, iterable: Iterable[Atom] = None):
        if not iterable:
            iterable = ()
        AtomSet.__init__(self, set(iterable))

    def add(self, atom: Atom) -> None:
        self._set.add(atom)

    def discard(self, atom: Atom) -> None:
        self._set.discard(atom)

    def __repr__(self) -> str:
        return "MutableAtomSet: "+str(self)
