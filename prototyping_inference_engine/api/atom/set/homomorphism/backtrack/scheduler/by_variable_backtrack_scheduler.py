from collections import Counter
from typing import Optional, cast

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.backtrack_scheduler import BacktrackScheduler
from prototyping_inference_engine.api.atom.set.index.index_provider import IndexProvider, IndexByTermProvider
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


class ByVariableBacktrackScheduler(BacktrackScheduler):
    def __init__(self, from_atom_set: AtomSet, index_provider: Optional[IndexProvider] = None):
        BacktrackScheduler.__init__(self, from_atom_set)
        self._order: list[Atom] = []

        if index_provider is None:
            index_provider = IndexByTermProvider()

        from prototyping_inference_engine.api.atom.set.index.index_by_term import IndexByTerm
        index = cast(IndexByTerm, index_provider.get_index(from_atom_set))

        if from_atom_set:
            first_atom = Counter({a: len(a.variables) for a in from_atom_set}).most_common(1)[0][0]
            as_copy = set(from_atom_set) - {first_atom}
            variable_counter: Counter[Variable] = Counter[Variable]()
            used_variables: set[Variable] = set[Variable]()
            self._add_atom_to_order(variable_counter, used_variables, first_atom)

            if not variable_counter:
                self._order += as_copy
                return

            already_treated_atoms = {first_atom}
            while as_copy:
                v = variable_counter.most_common(1)[0][0]
                del variable_counter[v]
                used_variables.add(v)
                for a in index.atoms_by_term(v):
                    if a in already_treated_atoms:
                        continue
                    self._add_atom_to_order(variable_counter, used_variables, a)
                    as_copy.remove(a)
                    already_treated_atoms.add(a)

    def _add_atom_to_order(self, variable_counter: Counter, used_variables: set[Variable], atom: Atom):
        variable_counter.update(v for v in atom.variables if v not in used_variables)
        self._order.append(atom)

    def has_next_atom(self, level: int) -> bool:
        return level < len(self._order)

    def next_atom(self, sub: Substitution, level: int) -> Atom:
        return self._order[level]
