"""
Created on 26 déc. 2021

@author: guillaume
"""

from collections.abc import Set as AbcSet
from typing import Set, Iterator

from api.atom.atom import Atom
from api.atom.term.constant import Constant
from api.atom.term.term import Term
from api.atom.term.variable import Variable


class AtomSet(AbcSet[Atom]):
    def __init__(self, s):
        self._set = s

    def __contains__(self, atom) -> bool:
        return atom in self._set

    def __iter__(self) -> Iterator[Atom]:
        return self._set.__iter__()

    def __len__(self) -> int:
        return len(self._set)

    @property
    def terms(self) -> Set[Term]:
        return {t for a in self for t in a.terms}

    @property
    def variables(self) -> Set[Variable]:
        return {v for v in
                filter(lambda t: isinstance(t, Variable),
                       self.terms)}

    @property
    def constants(self) -> Set[Constant]:
        return {v for v in
                filter(lambda t: isinstance(t, Constant),
                       self.terms)}

    def __str__(self):
        return "{"+(", ".join(map(str, self._set)))+"}"
