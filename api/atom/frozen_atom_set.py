'''
Created on 26 déc. 2021

@author: guillaume
'''
from collections.abc import Iterable
from functools import cached_property
from collections.abc import Hashable

from api.atom.atom_set import AtomSet
from api.atom.atom import Atom
from api.atom.term.constant import Constant
from api.atom.term.term import Term
from api.atom.term.variable import Variable


class FrozenAtomSet(AtomSet, Hashable):
    def __init__(self, iterable: Iterable[Atom] = None):
        if not iterable:
            iterable = ()
        AtomSet.__init__(self, frozenset(iterable))

    def __repr__(self) -> str:
        return "FrozenAtomSet: "+str(self)

    def __hash__(self) -> int:
        return hash(self._set)

    @cached_property
    def terms(self) -> set[Term]:
        return super().terms

    @cached_property
    def variables(self) -> set[Variable]:
        return super().variables

    @cached_property
    def constants(self) -> set[Constant]:
        return super().constants
