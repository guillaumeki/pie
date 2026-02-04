from functools import cache
from typing import Iterator, Optional

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.backtrack_scheduler import (
    BacktrackScheduler,
)
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.dynamic_backtrack_scheduler import (
    DynamicBacktrackScheduler,
)
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import (
    HomomorphismAlgorithm,
)
from prototyping_inference_engine.api.atom.set.index.index import Index
from prototyping_inference_engine.api.atom.set.index.index_provider import (
    IndexProvider,
    IndexByPredicateProvider,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution


class NaiveBacktrackHomomorphismAlgorithm(HomomorphismAlgorithm):
    def __init__(self, index_provider: Optional[IndexProvider] = None):
        if index_provider is None:
            index_provider = IndexByPredicateProvider()
        self._index_provider = index_provider

    @staticmethod
    @cache
    def instance() -> "NaiveBacktrackHomomorphismAlgorithm":
        return NaiveBacktrackHomomorphismAlgorithm()

    def compute_homomorphisms(
        self,
        from_atom_set: AtomSet,
        to_atom_set: AtomSet,
        sub: Optional[Substitution] = None,
        scheduler: Optional[BacktrackScheduler] = None,
    ) -> Iterator[Substitution]:
        if sub is None:
            sub = Substitution()

        if not from_atom_set.predicates.issubset(to_atom_set.predicates):
            return iter([])

        index = self._index_provider.get_index(to_atom_set)

        if scheduler is None:
            scheduler = DynamicBacktrackScheduler(from_atom_set)

        return self._compute_homomorphisms(index, sub, scheduler)

    def _compute_homomorphisms(
        self,
        index: Index,
        sub: Substitution,
        scheduler: BacktrackScheduler,
        position: int = 0,
    ) -> Iterator[Substitution]:
        if not scheduler.has_next_atom(position):
            yield sub
        else:
            next_atom = scheduler.next_atom(sub, position)
            for new_sub in index.extend_substitution(next_atom, sub):
                yield from self._compute_homomorphisms(
                    index, new_sub, scheduler, position + 1
                )
