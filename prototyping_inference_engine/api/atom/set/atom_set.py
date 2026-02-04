"""
Created on 26 déc. 2021

@author: guillaume
"""
from collections.abc import Set as AbcSet
from typing import Optional, Set, Iterator, Type, TypeVar, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.substitution.substitutable import Substitutable

T = TypeVar("T", bound=Term)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.constant import Constant
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class AtomSet(AbcSet[Atom], Substitutable["AtomSet"]):
    def __init__(self, s: AbcSet[Atom]):
        self._set = s

    def __contains__(self, atom: object) -> bool:
        return atom in self._set

    def __iter__(self) -> Iterator[Atom]:
        return self._set.__iter__()

    def __len__(self) -> int:
        return len(self._set)

    @property
    def terms(self) -> Set[Term]:
        return {t for a in self for t in a.terms}

    def terms_of_type(self, term_type: Type[T]) -> Set[T]:
        """Return all terms that are instances of the given type."""
        return {t for t in self.terms if isinstance(t, term_type)}

    @property
    def variables(self) -> Set["Variable"]:
        from prototyping_inference_engine.api.atom.term.variable import Variable
        return self.terms_of_type(Variable)

    @property
    def constants(self) -> Set["Constant"]:
        from prototyping_inference_engine.api.atom.term.constant import Constant
        return self.terms_of_type(Constant)

    @property
    def predicates(self) -> Set[Predicate]:
        return {a.predicate for a in self}

    def apply_substitution(self, substitution: "Substitution") -> "AtomSet":
        return self.__class__({a.apply_substitution(substitution) for a in self})

    def match(self, atom: Atom, sub: Optional["Substitution"] = None) -> Iterator[Atom]:
        from prototyping_inference_engine.api.atom.atom_operations import specialize
        for a in filter(lambda x: specialize(atom, x, sub) is not None, self._set):
            yield a

    def __str__(self):
        return " \u2227 ".join(map(str, self._set))

    def __repr__(self):
        return "<AtomSet: "+(" \u2227 ".join(map(str, self._set)))+">"
