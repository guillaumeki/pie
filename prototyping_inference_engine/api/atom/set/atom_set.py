"""
Created on 26 déc. 2021

@author: guillaume
"""

from collections.abc import Set as AbcSet
from typing import Set, Iterator

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


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

    @property
    def predicates(self) -> Set[Predicate]:
        return {a.predicate for a in self}

    def match(self, atom: Atom, sub: Substitution = None) -> Iterator[Atom]:
        for a in filter(lambda x: Substitution.specialize(atom, x, sub) is not None, self._set):
            yield a

    def __str__(self):
        return " \u2227 ".join(map(str, self._set))

    def __repr__(self):
        return "<AtomSet: "+(" \u2227 ".join(map(str, self._set)))+">"
