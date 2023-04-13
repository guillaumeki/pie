from collections import defaultdict
from typing import Iterator

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.index.index import Index
from prototyping_inference_engine.api.substitution.substitution import Substitution


class IndexByPredicate(Index):
    def __init__(self, atom_set: AtomSet):
        index = defaultdict(set)
        for atom in atom_set:
            index[atom.predicate].add(atom)
        self._predicate_index: defaultdict[Predicate, frozenset[Atom]] = defaultdict(frozenset)

        for p in index:
            self._predicate_index[p] = frozenset(index[p])

    def atoms_by_predicate(self, p: Predicate) -> frozenset[Atom]:
        return self._predicate_index[p]

    def domain(self, atom: Atom, sub: Substitution) -> frozenset[Atom]:
        return self.atoms_by_predicate(atom.predicate)
