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
from api.query.substitution import Substitution


class AtomSet(AbcSet[Atom]):
    def __init__(self, s):
        self._set = s

    def __contains__(self, atom: Atom) -> bool:
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

    def match(self, atom: Atom, sub: Substitution = None) -> Iterator[Atom]:
        frozen_variables = sub.image if sub else None
        for a in filter(lambda x: x.is_more_specific_than(atom, frozen_variables), self._set):
            yield a

    def __str__(self):
        return "{"+(", ".join(map(str, self._set)))+"}"
