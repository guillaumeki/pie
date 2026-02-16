#
# References:
# - "Foundations of Databases" —
#   Serge Abiteboul, Richard Hull, Victor Vianu.
#   Link: https://dl.acm.org/doi/book/10.5555/64510
#
# Summary:
# Conjunctive query answering can be characterized by the existence of a
# homomorphism from the query body to the database instance.
#
# Properties used here:
# - Homomorphism-based semantics for conjunctive queries.
#
# Implementation notes:
# This abstract interface defines the homomorphism computation contract used by
# CQ evaluation and query rewriting components.

from abc import ABC, abstractmethod
from typing import Iterator, Optional

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.scheduler.backtrack_scheduler import (
    BacktrackScheduler,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution


class HomomorphismAlgorithm(ABC):
    @abstractmethod
    def compute_homomorphisms(
        self,
        from_atom_set: AtomSet,
        to_atom_set: AtomSet,
        sub: Optional[Substitution] = None,
        scheduler: Optional[BacktrackScheduler] = None,
    ) -> Iterator[Substitution]:
        pass

    def exist_homomorphism(
        self,
        from_atom_set: AtomSet,
        to_atom_set: AtomSet,
        sub: Optional[Substitution] = None,
        scheduler: Optional[BacktrackScheduler] = None,
    ) -> bool:
        try:
            next(
                iter(
                    self.compute_homomorphisms(
                        from_atom_set, to_atom_set, sub, scheduler
                    )
                )
            )
        except StopIteration:
            return False

        return True
