"""
Evaluator for UnionQuery (disjunction of queries).
"""

from typing import Iterator, Type, Optional, TYPE_CHECKING, Iterable

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator import (
    QueryEvaluator,
)
from prototyping_inference_engine.api.query.prepared_query import PreparedQuery

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.query.query import Query
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator_registry import (
        QueryEvaluatorRegistry,
    )


class UnionQueryEvaluator(QueryEvaluator[UnionQuery]):
    """
    Evaluator for UnionQuery (disjunction of queries).

    A UnionQuery is satisfied if at least one of the sub-queries is satisfied.
    Returns the union of results from all sub-queries, deduplicated.

    The evaluator delegates evaluation of each sub-query to the appropriate
    evaluator from the registry based on the sub-query type.
    """

    def __init__(self, registry: Optional["QueryEvaluatorRegistry"] = None):
        """
        Create a UnionQueryEvaluator.

        Args:
            registry: The query evaluator registry. If None, uses the singleton.
        """
        self._registry = registry

    def _get_registry(self) -> "QueryEvaluatorRegistry":
        """Get the registry, using singleton if not provided."""
        if self._registry is not None:
            return self._registry
        from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator_registry import (
            QueryEvaluatorRegistry,
        )

        return QueryEvaluatorRegistry.instance()

    @classmethod
    def supported_query_type(cls) -> Type[UnionQuery]:
        return UnionQuery

    def evaluate(
        self,
        query: UnionQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        """
        Evaluate a UnionQuery against a data source.

        Evaluates each sub-query and yields the union of all results,
        with deduplication.

        Args:
            query: The UnionQuery to evaluate
            data: The data source to query
            substitution: An optional initial substitution

        Yields:
            Substitutions that satisfy at least one sub-query
        """
        prepared = self.prepare(query, data)
        from prototyping_inference_engine.api.substitution.substitution import (
            Substitution,
        )

        initial = substitution if substitution is not None else Substitution()
        yield from prepared.execute(initial)

    def evaluate_and_project(
        self,
        query: UnionQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator[tuple[Term, ...]]:
        """
        Evaluate a UnionQuery and project results onto answer variables.

        Args:
            query: The UnionQuery to evaluate
            data: The data source to query
            substitution: An optional initial substitution

        Yields:
            Deduplicated tuples of terms for answer variables
        """
        seen: set[tuple[Term, ...]] = set()

        for result_sub in self.evaluate(query, data, substitution):
            answer = tuple(result_sub.apply(v) for v in query.answer_variables)
            if answer not in seen:
                seen.add(answer)
                yield answer

    def prepare(
        self,
        query: UnionQuery,
        data: "ReadableData",
    ) -> (
        "PreparedQuery[UnionQuery, ReadableData, Iterable[Substitution], Substitution]"
    ):
        registry = self._get_registry()
        prepared_queries = []

        for sub_query in query.queries:
            evaluator = registry.get_evaluator(sub_query)
            if evaluator is None:
                raise ValueError(
                    f"No evaluator registered for query type: {type(sub_query).__name__}"
                )
            prepared_queries.append(evaluator.prepare(sub_query, data))

        return _PreparedUnionQuery(query, data, prepared_queries)


class _PreparedUnionQuery(
    PreparedQuery[UnionQuery, "ReadableData", Iterable["Substitution"], "Substitution"]
):
    def __init__(
        self,
        query: UnionQuery,
        data: "ReadableData",
        prepared_queries: list[
            PreparedQuery[
                "Query", "ReadableData", Iterable["Substitution"], "Substitution"
            ]
        ],
    ):
        self._query = query
        self._data = data
        self._prepared = prepared_queries

    @property
    def query(self) -> UnionQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._data

    def execute(self, assignation: "Substitution") -> Iterable["Substitution"]:
        seen: set[frozenset] = set()
        for prepared in self._prepared:
            for result_sub in prepared.execute(assignation):
                key = frozenset(result_sub.items())
                if key not in seen:
                    seen.add(key)
                    yield result_sub

    def estimate_bound(self, assignation: "Substitution") -> int | None:
        total = 0
        for prepared in self._prepared:
            bound = prepared.estimate_bound(assignation)
            if bound is None:
                return None
            total += bound
        return total
