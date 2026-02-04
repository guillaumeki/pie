from math import inf
from typing import Optional

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.backtrack_scheduler import (
    BacktrackScheduler,
)
from prototyping_inference_engine.api.atom.set.index.index_provider import (
    IndexProvider,
    BestAvailableIndexProvider,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution


class DynamicBacktrackScheduler(BacktrackScheduler):
    def __init__(
        self, from_atom_set: AtomSet, index_provider: Optional[IndexProvider] = None
    ):
        BacktrackScheduler.__init__(self, from_atom_set)
        self._order: list[Atom] = []
        self._not_ordered = set(from_atom_set)

        if index_provider is None:
            index_provider = BestAvailableIndexProvider()

        self._index = index_provider.get_index(from_atom_set)

    def has_next_atom(self, level: int) -> bool:
        return level < len(self._order) + len(self._not_ordered)

    def next_atom(self, sub: Substitution, level: int) -> Atom:
        while level + 1 < len(self._order):
            self._not_ordered.add(self._order.pop())
        if level + 1 == len(self._order):
            return self._order[level]

        next_a: Optional[Atom] = None
        smallest = inf
        for a in self._not_ordered:
            size = self._index.domain_size(a, sub)
            if smallest > size:
                next_a = a
                smallest = size

        if next_a is None:
            raise ValueError("No atom available for scheduling.")
        self._order.append(next_a)
        self._not_ordered.remove(next_a)

        return self._order[level]
