from functools import cache

from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.core.naive_core_by_specialization import NaiveCoreBySpecialization
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import ConjunctiveQueryContainment


class RedundanciesCleanerConjunctiveQuery:
    def __init__(self, core_algorithm: CoreAlgorithm = None, cq_query_containment: ConjunctiveQueryContainment = None):
        if core_algorithm:
            self._core_algorithm: CoreAlgorithm = core_algorithm
        else:
            self._core_algorithm: CoreAlgorithm = NaiveCoreBySpecialization.instance()

        if cq_query_containment:
            self._cq_query_containment = cq_query_containment
        else:
            self._cq_query_containment = ConjunctiveQueryContainment.instance()

    @staticmethod
    @cache
    def instance(core_algorithm: CoreAlgorithm = None,
                 cq_query_containment: ConjunctiveQueryContainment = None) -> "RedundanciesCleanerConjunctiveQuery":
        return RedundanciesCleanerConjunctiveQuery(core_algorithm, cq_query_containment)

    def compute_core(self, cq: ConjunctiveQuery) -> ConjunctiveQuery:
        core_atom_set = self._core_algorithm.compute_core(cq.atoms, cq.answer_variables)
        return ConjunctiveQuery(core_atom_set, cq.answer_variables, cq.label, cq.pre_substitution)

    def compute_cover(self, scq: set[ConjunctiveQuery], del_redundancies_in_cqs: bool = True) \
            -> set[ConjunctiveQuery]:
        cover: set[ConjunctiveQuery] = set()
        for cq_to_test in scq:
            to_remove = set()
            add = True
            for cq_in_cover in cover:
                if self._cq_query_containment.is_contained_in(cq_to_test, cq_in_cover):
                    add = False
                    break
                elif self._cq_query_containment.is_contained_in(cq_in_cover, cq_to_test):
                    to_remove.add(cq_in_cover)
            cover -= to_remove
            if add:
                if del_redundancies_in_cqs:
                    cq_to_test = self.compute_core(cq_to_test)
                cover.add(cq_to_test)

        return cover

    def remove_more_specific_than(self,
                                  scq1: set[ConjunctiveQuery],
                                  scq2: set[ConjunctiveQuery]) -> set[ConjunctiveQuery]:
        new_scq = set()
        for cq1 in scq1:
            if all(not self._cq_query_containment.is_contained_in(cq1, cq2) for cq2 in scq2):
                new_scq.add(cq1)
        return new_scq
