from functools import cache
from typing import Optional

from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.core.core_algorithm_provider import (
    CoreAlgorithmProvider, DefaultCoreAlgorithmProvider
)
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import ConjunctiveQueryContainment
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment_provider import (
    ConjunctiveQueryContainmentProvider, DefaultCQContainmentProvider
)


class RedundanciesCleanerConjunctiveQuery:
    def __init__(self,
                 core_algorithm_provider: Optional[CoreAlgorithmProvider] = None,
                 cq_containment_provider: Optional[ConjunctiveQueryContainmentProvider] = None):
        if core_algorithm_provider is None:
            core_algorithm_provider = DefaultCoreAlgorithmProvider()
        self._core_algorithm: CoreAlgorithm = core_algorithm_provider.get_algorithm()

        if cq_containment_provider is None:
            cq_containment_provider = DefaultCQContainmentProvider()
        self._cq_query_containment: ConjunctiveQueryContainment = cq_containment_provider.get_containment()

    @staticmethod
    @cache
    def instance() -> "RedundanciesCleanerConjunctiveQuery":
        return RedundanciesCleanerConjunctiveQuery()

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
