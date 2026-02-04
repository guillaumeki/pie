from functools import cache
from typing import Optional, Protocol, runtime_checkable

from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import (
    ConjunctiveQueryContainment,
)
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment_provider import (
    ConjunctiveQueryContainmentProvider,
    DefaultCQContainmentProvider,
)
from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_conjunctive_query import (
    RedundanciesCleanerConjunctiveQuery,
)
from prototyping_inference_engine.api.query.union_query import UnionQuery


@runtime_checkable
class CQRedundanciesCleanerProvider(Protocol):
    """Protocol for providing a RedundanciesCleanerConjunctiveQuery."""

    def get_cleaner(self) -> RedundanciesCleanerConjunctiveQuery: ...


class DefaultCQRedundanciesCleanerProvider:
    """Provides default RedundanciesCleanerConjunctiveQuery."""

    def get_cleaner(self) -> RedundanciesCleanerConjunctiveQuery:
        return RedundanciesCleanerConjunctiveQuery.instance()


class RedundanciesCleanerUnionConjunctiveQueries:
    def __init__(
        self,
        cq_containment_provider: Optional[ConjunctiveQueryContainmentProvider] = None,
        cq_cleaner_provider: Optional[CQRedundanciesCleanerProvider] = None,
    ):
        if cq_cleaner_provider is None:
            cq_cleaner_provider = DefaultCQRedundanciesCleanerProvider()
        self._cq_redundancies_cleaner: RedundanciesCleanerConjunctiveQuery = (
            cq_cleaner_provider.get_cleaner()
        )

        if cq_containment_provider is None:
            cq_containment_provider = DefaultCQContainmentProvider()
        self._cq_query_containment: ConjunctiveQueryContainment = (
            cq_containment_provider.get_containment()
        )

    @staticmethod
    @cache
    def instance() -> "RedundanciesCleanerUnionConjunctiveQueries":
        return RedundanciesCleanerUnionConjunctiveQueries()

    def compute_cover(
        self, ucq: UnionQuery[ConjunctiveQuery], del_redundancies_in_cqs: bool = True
    ) -> UnionQuery[ConjunctiveQuery]:
        return UnionQuery(
            self._cq_redundancies_cleaner.compute_cover(
                set(ucq.conjunctive_queries), del_redundancies_in_cqs
            ),
            ucq.answer_variables,
            ucq.label,
        )

    def remove_more_specific_than(
        self, ucq1: UnionQuery[ConjunctiveQuery], ucq2: UnionQuery[ConjunctiveQuery]
    ) -> UnionQuery[ConjunctiveQuery]:
        return UnionQuery(
            self._cq_redundancies_cleaner.remove_more_specific_than(
                set(ucq1.conjunctive_queries),
                set(ucq2.conjunctive_queries),
            ),
            ucq1.answer_variables,
            ucq1.label,
        )
