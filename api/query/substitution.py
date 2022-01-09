from copy import copy
from functools import cache
from typing import Union

from api.atom.atom import Atom
from api.atom.atom_set import AtomSet
from api.atom.term.term import Term
from api.atom.term.variable import Variable


class Substitution:
    def __init__(self, initial: Union["Substitution", dict[Variable, Term]] = None):
        match initial:
            case Substitution():
                self._sub = initial._sub  # type: ignore
            case dict():
                self._sub = copy(initial)
            case _:
                self._sub = dict()

    @cache
    @property
    def graph(self) -> frozenset[tuple[Variable, Term]]:
        return frozenset(self._sub.items())

    @cache
    @property
    def domain(self) -> frozenset[Variable]:
        return frozenset(self._sub.keys())

    @cache
    @property
    def image(self) -> frozenset[Term]:
        return frozenset(self._sub.values())

    def apply(self, other: Union[Variable, Atom, AtomSet]) -> Union[Term, Atom, AtomSet]:
        match other:
            case Variable():
                if other in self.domain:
                    return self._sub[other]
                else:
                    return other
            case Atom():
                return Atom(other.predicate, (self(t) for t in other.terms))  # type: ignore
            case AtomSet():
                return other.__class__({self(a) for a in other})  # type: ignore
            case _:
                return other

    def compose(self, sub: "Substitution") -> "Substitution":
        new_sub = {}

        for k, v in sub.graph:
            new_sub[k] = self(v)
        for k, v in self.graph:
            if k not in new_sub:
                new_sub[k] = v

        # Remove the cases where k = v
        new_sub = {k: v for k, v in filter(lambda x, y: x != y, new_sub.items())}

        return Substitution(new_sub)

    def __call__(self, other: Union["Substitution", Variable, Atom, AtomSet])\
            -> Union["Substitution", Term, Atom, AtomSet]:
        match other:
            case Substitution():
                return self.compose(other)
            case _:
                return self.apply(other)

