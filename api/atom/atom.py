"""
Created on 23 déc. 2021

@author: guillaume
"""
from typing import Set

from api.atom.predicate import Predicate
from api.atom.term.constant import Constant
from api.atom.term.term import Term
from api.atom.term.variable import Variable


class Atom:
    def __init__(self, predicate: Predicate, *terms: Term):
        self._predicate = predicate
        self._terms = terms

    @property
    def predicate(self) -> Predicate:
        return self._predicate

    @property
    def terms(self) -> tuple[Term, ...]:
        return self._terms

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

    def is_more_specific_than(self, other: "Atom", freeze: frozenset[Variable] = ()) -> bool:
        if self.predicate != other.predicate:
            return False

        for i in range(self.predicate.arity):
            match other.terms[i]:
                case Constant():
                    if other.terms[i] != self.terms[i]:
                        return False
                case Variable():
                    if other.terms[i] in freeze and other.terms[i] != self.terms[i]:
                        return False
                    #TODO: To complete

        return True

    def __getitem__(self, item: int):
        return self._terms[item]

    def __repr__(self) -> str:
        return str(self.predicate)\
            + "(" + ", ".join(map(str, self.terms)) + ")"

    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False
        else:
            return self.predicate == other.predicate and self.terms == other.terms

    def __hash__(self):
        return hash((self.predicate, self.terms))
