from functools import cache

from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import ConjunctiveQueryContainment
from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_conjunctive_query import RedundanciesCleanerConjunctiveQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries


class RedundanciesCleanerUnionConjunctiveQueries:
    def __init__(self,
                 cq_query_containment: ConjunctiveQueryContainment = None,
                 cq_redundancies_cleaner: RedundanciesCleanerConjunctiveQuery = None):
        if cq_redundancies_cleaner:
            self._cq_redundancies_cleaner = cq_redundancies_cleaner
        else:
            self._cq_redundancies_cleaner = RedundanciesCleanerConjunctiveQuery.instance()

        if cq_query_containment:
            self._cq_query_containment = cq_query_containment
        else:
            self._cq_query_containment = ConjunctiveQueryContainment.instance()

    @staticmethod
    @cache
    def instance(cq_query_containment: ConjunctiveQueryContainment = None,
                 cq_redundancies_cleaner: RedundanciesCleanerConjunctiveQuery = None) \
            -> "RedundanciesCleanerUnionConjunctiveQueries":
        return RedundanciesCleanerUnionConjunctiveQueries(cq_query_containment, cq_redundancies_cleaner)

    def compute_cover(self, ucq: UnionConjunctiveQueries, del_redundancies_in_cqs: bool = True) \
            -> UnionConjunctiveQueries:
        return UnionConjunctiveQueries(
            self._cq_redundancies_cleaner.compute_cover(ucq.conjunctive_queries, del_redundancies_in_cqs),
            ucq.answer_variables,
            ucq.label)

    def remove_more_specific_than(self,
                                  ucq1: UnionConjunctiveQueries,
                                  ucq2: UnionConjunctiveQueries) -> UnionConjunctiveQueries:
        return UnionConjunctiveQueries(
            self._cq_redundancies_cleaner.remove_more_specific_than(ucq1.conjunctive_queries, ucq2.conjunctive_queries),
            ucq1.answer_variables,
            ucq1.label)
