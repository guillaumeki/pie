from collections import defaultdict
from typing import Iterator

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.substitution.substitution import Substitution


class IndexByPredicate:
    def __init__(self, atom_set: AtomSet):
        index = defaultdict(set)
        for atom in atom_set:
            index[atom.predicate].add(atom)
        self._index: defaultdict[Predicate, frozenset[Atom]] = defaultdict(frozenset)

        for p in index:
            self._index[p] = frozenset(index[p])

    def atoms_by_predicate(self, p: Predicate) -> frozenset[Atom]:
        return self._index[p]

    def match(self, atom: Atom, sub: Substitution = None) -> Iterator[Atom]:
        if sub is None:
            sub = Substitution()
        for a in self.atoms_by_predicate(atom.predicate):
            if Substitution.specialize(atom, a, sub) is not None:
                yield a

    def extend_substitution(self, atom: Atom, sub: Substitution) -> Iterator[Substitution]:
        for a in self.atoms_by_predicate(atom.predicate):
            spec = Substitution.specialize(atom, a, sub)
            if spec is not None:
                yield spec
