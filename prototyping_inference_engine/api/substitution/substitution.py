from collections.abc import Set
from typing import Union, TypeVar
from collections.abc import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitutable import Substitutable

S1 = TypeVar("S1", Term, Atom, Set[Atom], Substitutable)
S2 = TypeVar("S2", "Substitution", Term, Atom, Set[Atom], Iterable, Substitutable)


class Substitution(dict[Variable, Term]):
    def __init__(self, initial: Union["Substitution", dict[Variable, Term]] = None):
        if initial is None:
            initial = {}
        super().__init__(initial)

    @property
    def graph(self):
        return self.items()

    @property
    def domain(self):
        return self.keys()

    @property
    def image(self):
        return self.values()

    def restrict_to(self, variables: Iterable[Variable]) -> "Substitution":
        return Substitution({v: self(v) for v in variables if v != self(v)})

    def apply(self, other: S1) -> S1:
        match other:
            case Variable():
                if other in self.domain:
                    return self[other]
                else:
                    return other
            case Atom():
                return Atom(other.predicate, *(self(t) for t in other.terms))  # type: ignore
            case Substitutable():
                return other.apply_substitution(self)
            case Set() | Iterable():
                return other.__class__({self(a) for a in other})  # type: ignore
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
        new_sub = {k: v for k, v in filter(lambda x: x[0] != x[1], new_sub.items())}

        return Substitution(new_sub)

    def aggregate(self, sub: "Substitution") -> "Substitution":
        return Substitution(self | sub)

    def __call__(self, other: S2) -> S2:
        match other:
            case Substitution():
                return self.compose(other)
            case _:
                return self.apply(other)

    @staticmethod
    def safe_renaming(variables: Iterable[Variable]) -> "Substitution":
        return Substitution({v: Variable.safe_renaming(v) for v in variables})

    @staticmethod
    def specialize(from_atom: Atom, to_atom: Atom, sub: "Substitution" = None) -> "Optionnal[Substitution]":
        if from_atom.predicate != to_atom.predicate:
            return None

        sub = Substitution(sub)

        for i in range(from_atom.predicate.arity):
            match from_atom.terms[i]:
                case Constant():
                    if from_atom.terms[i] != to_atom.terms[i]:
                        return None
                case Variable():
                    if from_atom.terms[i] in sub.domain and sub(from_atom.terms[i]) != to_atom.terms[i]:
                        return None
                    sub[from_atom.terms[i]] = to_atom.terms[i]

        return sub

    def __str__(self):
        return "{" + ", ".join(f"{v} \u21A6 {t}" for v, t in self.graph) + "}"

    def __repr__(self):
        return f"<Substitution:{str(self)}>"
