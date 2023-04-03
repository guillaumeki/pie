from functools import cache

from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import HomomorphismAlgorithm
from prototyping_inference_engine.api.atom.set.homomorphism.naive_backtrack_homomorphism_algorithm import NaiveBacktrackHomomorphismAlgorithm
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.containment.query_containment import QueryContainment


class ConjunctiveQueryContainment(QueryContainment[ConjunctiveQuery]):
    def __init__(self, homomorphism_algorithm: HomomorphismAlgorithm = None):
        if homomorphism_algorithm:
            self._homomorphism_algorithm: HomomorphismAlgorithm = homomorphism_algorithm
        else:
            self._homomorphism_algorithm: HomomorphismAlgorithm = NaiveBacktrackHomomorphismAlgorithm.instance()

    @staticmethod
    @cache
    def instance() -> "ConjunctiveQueryContainment":
        return ConjunctiveQueryContainment()

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
