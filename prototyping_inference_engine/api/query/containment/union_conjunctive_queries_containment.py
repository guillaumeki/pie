from functools import cache
from typing import Optional

from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import (
    ConjunctiveQueryContainment,
)
from prototyping_inference_engine.api.query.containment.conjunctive_query_containment_provider import (
    ConjunctiveQueryContainmentProvider,
    DefaultCQContainmentProvider,
)
from prototyping_inference_engine.api.query.containment.query_containment import (
    QueryContainment,
)
from prototyping_inference_engine.api.query.union_query import UnionQuery


class UnionConjunctiveQueriesContainment(
    QueryContainment[UnionQuery[ConjunctiveQuery]]
):
    def __init__(
        self,
        cq_containment_provider: Optional[ConjunctiveQueryContainmentProvider] = None,
    ):
        if cq_containment_provider is None:
            cq_containment_provider = DefaultCQContainmentProvider()
        self._cq_containment: ConjunctiveQueryContainment = (
            cq_containment_provider.get_containment()
        )

    @staticmethod
    @cache
    def instance() -> "UnionConjunctiveQueriesContainment":
        return UnionConjunctiveQueriesContainment()

    def is_contained_in(
        self, ucq1: UnionQuery[ConjunctiveQuery], ucq2: UnionQuery[ConjunctiveQuery]
    ) -> bool:
        if len(ucq1.answer_variables) != len(ucq2.answer_variables):
            return False

        return all(
            any(self._cq_containment.is_contained_in(q1, q2) for q2 in ucq2)
            for q1 in ucq1
        )
