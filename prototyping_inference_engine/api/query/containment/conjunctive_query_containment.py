from functools import cache
from typing import Protocol, runtime_checkable, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import HomomorphismAlgorithm
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm_provider import (
    HomomorphismAlgorithmProvider, DefaultHomomorphismAlgorithmProvider
)
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery

if TYPE_CHECKING:
    pass


@runtime_checkable
class ConjunctiveQueryContainment(Protocol):
    """Protocol for conjunctive query containment checking."""

    def is_contained_in(self, q1: ConjunctiveQuery, q2: ConjunctiveQuery) -> bool:
        ...

    def is_equivalent_to(self, q1: ConjunctiveQuery, q2: ConjunctiveQuery) -> bool:
        ...


class HomomorphismBasedCQContainment:
    """Conjunctive query containment implementation using homomorphism checking."""

    def __init__(self, algorithm_provider: Optional[HomomorphismAlgorithmProvider] = None):
        if algorithm_provider is None:
            algorithm_provider = DefaultHomomorphismAlgorithmProvider()
        self._homomorphism_algorithm: HomomorphismAlgorithm = algorithm_provider.get_algorithm()

    @staticmethod
    @cache
    def instance() -> "HomomorphismBasedCQContainment":
        return HomomorphismBasedCQContainment()

    def is_contained_in(self, q1: ConjunctiveQuery, q2: ConjunctiveQuery) -> bool:
        if len(q1.answer_variables) != len(q2.answer_variables):
            return False

        try:
            pre_sub = next(iter(self._homomorphism_algorithm.compute_homomorphisms(
                FrozenAtomSet([q2.pre_substitution(q2.answer_atom)]),
                FrozenAtomSet([q1.pre_substitution(q1.answer_atom)]))))
        except StopIteration:
            return False

        return self._homomorphism_algorithm.exist_homomorphism(q2.atoms, q1.atoms, pre_sub)

    def is_equivalent_to(self, q1: ConjunctiveQuery, q2: ConjunctiveQuery) -> bool:
        return self.is_contained_in(q1, q2) and self.is_contained_in(q2, q1)
