from collections.abc import Iterable
from functools import cached_property
from collections.abc import Hashable
from typing import Iterator, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.index.index import Index
from prototyping_inference_engine.api.atom.set.index.index_by_term_and_predicate import IndexByTermAndPredicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class FrozenAtomSet(AtomSet, Hashable):
    def __init__(self, iterable: Optional[Iterable[Atom]] = None):
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

    @cached_property
    def predicates(self) -> set[Predicate]:
        return super(FrozenAtomSet, self).predicates

    @cached_property
    def index_by_term_and_predicate(self) -> IndexByTermAndPredicate:
        return IndexByTermAndPredicate(self)

    @property
    def index_by_term(self) -> IndexByTermAndPredicate:
        return self.index_by_term_and_predicate

    @property
    def index_by_predicate(self) -> IndexByTermAndPredicate:
        return self.index_by_term_and_predicate

    @property
    def index(self) -> Index:
        return self.index_by_term_and_predicate

    def match(self, atom: Atom, sub: Optional["Substitution"] = None) -> Iterator[Atom]:
        return self.index_by_term_and_predicate.match(atom, sub)

    def apply_substitution(self, substitution: "Substitution") -> "FrozenAtomSet":
        return FrozenAtomSet(a.apply_substitution(substitution) for a in self)
