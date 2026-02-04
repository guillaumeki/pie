"""
Created on 26 déc. 2021

@author: guillaume
"""
from collections.abc import MutableSet
from typing import Iterable, Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet


class MutableAtomSet(AtomSet, MutableSet):
    def __init__(self, iterable: Optional[Iterable[Atom]] = None):
        if not iterable:
            iterable = ()
        data = set(iterable)
        AtomSet.__init__(self, data)
        self._set: set[Atom] = data

    def add(self, atom: Atom) -> None:
        self._set.add(atom)

    def discard(self, atom: Atom) -> None:
        self._set.discard(atom)

    def __repr__(self) -> str:
        return "MutableAtomSet: "+str(self)
