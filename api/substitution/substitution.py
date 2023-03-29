from copy import copy
from functools import cache
from typing import Union, Iterable

from api.atom.atom import Atom
from api.atom.term.term import Term
from api.atom.term.variable import Variable
from api.substitution.substitutable import Substitutable


class Substitution(dict[Variable, Term]):
    def __init__(self, initial: Union["Substitution", dict[Variable, Term]] = None):
        super().__init__(initial)

    @property
    @cache
    def graph(self) -> frozenset[tuple[Variable, Term]]:
        return frozenset(self.items())

    @property
    @cache
    def domain(self) -> frozenset[Variable]:
        return frozenset(self.keys())

    @property
    @cache
    def image(self) -> frozenset[Term]:
        return frozenset(self.values())

    def apply(self, other: Union[Term, Atom, Iterable[Atom], Substitutable]) \
            -> Union[Term, Atom, Iterable[Atom], Substitutable]:
        match other:
            case Variable():
                if other in self.domain:
                    return self[other]
                else:
                    return other
            case Atom():
                return Atom(other.predicate, (self(t) for t in other.terms))  # type: ignore
            case Iterable():
                return other.__class__({self(a) for a in other})  # type: ignore
            case Substitutable():
                return other.apply_substitution(self)
            case _:
                return other

    def compose(self, sub: "Substitution") -> "Substitution":
        new_sub = {}

        for k, v in sub.graph:
            new_sub[k] = self.apply(v)
        for k, v in self.graph:
            if k not in new_sub:
                new_sub[k] = v

        # Remove the cases where k = v
        new_sub = {k: v for k, v in filter(lambda x, y: x != y, new_sub.items())}

        return Substitution(new_sub)

    def __call__(self, other: Union["Substitution", Term, Atom, Iterable[Atom], Substitutable])\
            -> Union["Substitution", Term, Atom, Iterable[Atom], Substitutable]:
        match other:
            case Substitution():
                return self.compose(other)
            case _:
                return self.apply(other)

    @staticmethod
    def safe_renaming(variables: Iterable[Variable]) -> "Substitution":
        return Substitution({v: Variable.fresh_variable() for v in variables})
