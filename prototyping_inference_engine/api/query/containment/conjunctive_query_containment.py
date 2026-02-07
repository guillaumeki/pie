from functools import cache
from typing import Protocol, runtime_checkable, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.predicate import SpecialPredicate
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import (
    HomomorphismAlgorithm,
)
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm_provider import (
    HomomorphismAlgorithmProvider,
    DefaultHomomorphismAlgorithmProvider,
)
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery

if TYPE_CHECKING:
    pass


@runtime_checkable
class ConjunctiveQueryContainment(Protocol):
    """Protocol for conjunctive query containment checking."""

    def is_contained_in(self, q1: ConjunctiveQuery, q2: ConjunctiveQuery) -> bool: ...

    def is_equivalent_to(self, q1: ConjunctiveQuery, q2: ConjunctiveQuery) -> bool: ...


class HomomorphismBasedCQContainment:
    """Conjunctive query containment implementation using homomorphism checking."""

    def __init__(
        self, algorithm_provider: Optional[HomomorphismAlgorithmProvider] = None
    ):
        if algorithm_provider is None:
            algorithm_provider = DefaultHomomorphismAlgorithmProvider()
        self._homomorphism_algorithm: HomomorphismAlgorithm = (
            algorithm_provider.get_algorithm()
        )

    @staticmethod
    @cache
    def instance() -> "HomomorphismBasedCQContainment":
        return HomomorphismBasedCQContainment()

    def is_contained_in(self, q1: ConjunctiveQuery, q2: ConjunctiveQuery) -> bool:
        normalized_q1 = self._normalize_equalities(q1)
        normalized_q2 = self._normalize_equalities(q2)
        if normalized_q1 is None:
            return True
        if normalized_q2 is None:
            return False

        if len(normalized_q1.answer_variables) != len(normalized_q2.answer_variables):
            return False

        try:
            pre_sub = next(
                iter(
                    self._homomorphism_algorithm.compute_homomorphisms(
                        FrozenAtomSet(
                            [normalized_q2.pre_substitution(normalized_q2.answer_atom)]
                        ),
                        FrozenAtomSet(
                            [normalized_q1.pre_substitution(normalized_q1.answer_atom)]
                        ),
                    )
                )
            )
        except StopIteration:
            return False

        return self._homomorphism_algorithm.exist_homomorphism(
            normalized_q2.atoms, normalized_q1.atoms, pre_sub
        )

    def is_equivalent_to(self, q1: ConjunctiveQuery, q2: ConjunctiveQuery) -> bool:
        return self.is_contained_in(q1, q2) and self.is_contained_in(q2, q1)

    @staticmethod
    def _normalize_equalities(
        query: ConjunctiveQuery,
    ) -> Optional[ConjunctiveQuery]:
        equality_predicate = SpecialPredicate.EQUALITY.value
        equality_atoms = [
            atom for atom in query.atoms if atom.predicate == equality_predicate
        ]
        if not equality_atoms:
            return query

        partition = TermPartition()
        for atom in equality_atoms:
            partition.union(atom.terms[0], atom.terms[1])

        if not partition.is_admissible:
            return None

        substitution = partition.associated_substitution(context=query)
        if substitution is None:
            return None

        normalized_atoms = [
            substitution.apply(atom)
            for atom in query.atoms
            if atom.predicate != equality_predicate
        ]
        pre_substitution = substitution.restrict_to(query.answer_variables)
        return ConjunctiveQuery(
            normalized_atoms,
            query.answer_variables,
            query.label,
            pre_substitution,
        )
