"""
Homomorphism algorithm that accounts for rule compilation.
"""

from __future__ import annotations

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
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.rule_compilation.api.rule_compilation import (
    RuleCompilation,
)


class CompilationAwareHomomorphismAlgorithm(HomomorphismAlgorithm):
    def __init__(self, compilation: RuleCompilation):
        self._compilation = compilation

    @classmethod
    @cache
    def instance(
        cls, compilation: RuleCompilation
    ) -> "CompilationAwareHomomorphismAlgorithm":
        return cls(compilation)

    def compute_homomorphisms(
        self,
        from_atom_set: AtomSet,
        to_atom_set: AtomSet,
        sub: Optional[Substitution] = None,
        scheduler: Optional[BacktrackScheduler] = None,
    ) -> Iterator[Substitution]:
        if sub is None:
            sub = Substitution()

        to_predicates = to_atom_set.predicates
        for pred in from_atom_set.predicates:
            if not (self._compilation.get_compatible_predicates(pred) & to_predicates):
                return iter([])

        atoms_by_predicate: dict = {}
        for atom in to_atom_set:
            atoms_by_predicate.setdefault(atom.predicate, set()).add(atom)

        if scheduler is None:
            scheduler = DynamicBacktrackScheduler(from_atom_set)

        return self._compute_homomorphisms(atoms_by_predicate, sub, scheduler)

    def _compute_homomorphisms(
        self,
        atoms_by_predicate: dict,
        sub: Substitution,
        scheduler: BacktrackScheduler,
        position: int = 0,
    ) -> Iterator[Substitution]:
        if not scheduler.has_next_atom(position):
            yield sub
            return

        next_atom = scheduler.next_atom(sub, position)
        for pred in self._compilation.get_compatible_predicates(next_atom.predicate):
            for candidate in atoms_by_predicate.get(pred, set()):
                for new_sub in self._compilation.get_homomorphisms(
                    next_atom, candidate, sub
                ):
                    yield from self._compute_homomorphisms(
                        atoms_by_predicate, new_sub, scheduler, position + 1
                    )
