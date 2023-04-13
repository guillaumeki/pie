from collections import defaultdict

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.index.index import Index
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.substitution.substitution import Substitution


class IndexByTerm(Index):
    def __init__(self, atom_set: AtomSet):
        index = defaultdict(set)
        for atom in atom_set:
            for t in atom.terms:
                index[t].add(atom)
        self._term_index: defaultdict[Term, frozenset[Atom]] = defaultdict(frozenset)
        self._atom_set = atom_set

        for v in index:
            self._term_index[v] = frozenset(index[v])

    def atoms_by_term(self, t: Term) -> frozenset[Atom]:
        return self._term_index[t]

    def domain(self, atom: Atom, sub: Substitution) -> frozenset[Atom]:
        smallest_domain = None
        for t in atom.terms:
            if ((isinstance(t, Constant)
                 and (smallest_domain is None or len(self.atoms_by_term(t)) < len(smallest_domain)))
                or (t in sub.domain
                    and (smallest_domain is None or len(self.atoms_by_term(sub(t))) < len(smallest_domain)))):
                smallest_domain = self.atoms_by_term(sub(t))

        return smallest_domain if smallest_domain is not None else self._atom_set
