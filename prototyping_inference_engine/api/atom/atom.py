"""
Created on 23 déc. 2021

@author: guillaume
"""
from typing import Set, TYPE_CHECKING

from prototyping_inference_engine.api.atom.predicate import Predicate, SpecialPredicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitutable import Substitutable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class Atom(Substitutable["Atom"]):
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

    def apply_substitution(self, substitution: "Substitution") -> "Atom":
        return Atom(self.predicate, *(t.apply_substitution(substitution) for t in self.terms))

    def __getitem__(self, item: int):
        return self._terms[item]

    def __repr__(self) -> str:
        if self.predicate == SpecialPredicate.EQUALITY.value:
            return f"{str(self.terms[0])}={str(self.terms[1])}"

        return str(self.predicate)\
            + "(" + ", ".join(map(str, self.terms)) + ")"

    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False
        else:
            return self.predicate == other.predicate and self.terms == other.terms

    def __hash__(self):
        return hash((self.predicate, self.terms))
