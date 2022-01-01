'''
Created on 26 déc. 2021

@author: guillaume
'''
from collections.abc import Iterable

from api.atom.atom_set import AtomSet
from api.atom.atom import Atom


class FrozenAtomSet(AtomSet):
    def __init__(self, iterable: Iterable[Atom] = None):
        if not iterable:
            iterable = ()
        super().__init__(frozenset(iterable))

    def __repr__(self) -> str:
        return "FrozenAtomSet: "+str(self)
