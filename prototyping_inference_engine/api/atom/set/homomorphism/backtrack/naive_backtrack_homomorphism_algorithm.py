from functools import cache
from typing import Iterator

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.by_variable_and_domain_backtrack_scheduler import \
    ByVariableAndDomainBacktrackScheduler
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.by_variable_backtrack_scheduler import \
    ByVariableBacktrackScheduler
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.backtrack_scheduler import BacktrackScheduler
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.dynamic_backtrack_scheduler import \
    DynamicBacktrackScheduler
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import HomomorphismAlgorithm
from prototyping_inference_engine.api.atom.set.index.index_by_predicate import IndexByPredicate
from prototyping_inference_engine.api.atom.set.index.index_by_term_and_predicate import IndexByTermAndPredicate
from prototyping_inference_engine.api.atom.set.index.indexed_by_predicate_atom_set import IndexedByPredicateAtomSet
from prototyping_inference_engine.api.substitution.substitution import Substitution


class NaiveBacktrackHomomorphismAlgorithm(HomomorphismAlgorithm):
    @staticmethod
    @cache
    def instance() -> "NaiveBacktrackHomomorphismAlgorithm":
        return NaiveBacktrackHomomorphismAlgorithm()

    def compute_homomorphisms(
            self,
            from_atom_set: AtomSet,
            to_atom_set: AtomSet,
            sub: Substitution = None,
            scheduler: BacktrackScheduler = None) \
            -> Iterator[Substitution]:
        if sub is None:
            sub = Substitution()

        if not from_atom_set.predicates.issubset(to_atom_set.predicates):
            return iter([])

        if isinstance(to_atom_set, IndexedByPredicateAtomSet):
            index = to_atom_set.index_by_predicate
        else:
            index = IndexByTermAndPredicate(to_atom_set)

        if scheduler is None:
            scheduler = DynamicBacktrackScheduler(from_atom_set)

        return self._compute_homomorphisms(index, sub, scheduler)

    def _compute_homomorphisms(self,
                               predicate_index: IndexByPredicate,
                               sub: Substitution,
                               scheduler: BacktrackScheduler,
                               position: int = 0) \
            -> Iterator[Substitution]:
        if not scheduler.has_next_atom(position):
            yield sub
        else:
            next_atom = scheduler.next_atom(sub, position)
            for new_sub in predicate_index.extend_substitution(next_atom, sub):
                yield from self._compute_homomorphisms(predicate_index, new_sub, scheduler, position + 1)
