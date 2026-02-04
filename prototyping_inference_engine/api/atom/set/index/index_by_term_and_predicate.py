from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.index.index_by_predicate import (
    IndexByPredicate,
)
from prototyping_inference_engine.api.atom.set.index.index_by_term import IndexByTerm
from prototyping_inference_engine.api.substitution.substitution import Substitution


class IndexByTermAndPredicate(IndexByTerm, IndexByPredicate):
    def __init__(self, atom_set: AtomSet):
        IndexByTerm.__init__(self, atom_set)
        IndexByPredicate.__init__(self, atom_set)

    def domain(self, atom: Atom, sub: Substitution) -> frozenset[Atom]:
        d1 = IndexByTerm.domain(self, atom, sub)
        d2 = IndexByPredicate.domain(self, atom, sub)
        if len(d1) < len(d2):
            return d1
        else:
            return d2
