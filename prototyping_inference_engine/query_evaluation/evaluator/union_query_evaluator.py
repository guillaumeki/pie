"""
Evaluator for UnionQuery (disjunction of queries).
"""
from typing import Iterator, Type, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.query_evaluation.evaluator.query_evaluator import QueryEvaluator

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.query_evaluator_registry import (
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
        from prototyping_inference_engine.query_evaluation.evaluator.query_evaluator_registry import (
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
        substitution: "Substitution" = None,
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
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        if substitution is None:
            substitution = Substitution()

        registry = self._get_registry()

        # Track seen results for deduplication
        seen: set[frozenset] = set()

        # Evaluate each sub-query
        for sub_query in query.queries:
            evaluator = registry.get_evaluator(sub_query)
            if evaluator is None:
                raise ValueError(
                    f"No evaluator registered for query type: {type(sub_query).__name__}"
                )

            for result_sub in evaluator.evaluate(sub_query, data, substitution):
                key = frozenset(result_sub.items())
                if key not in seen:
                    seen.add(key)
                    yield result_sub

    def evaluate_and_project(
        self,
        query: UnionQuery,
        data: "ReadableData",
        substitution: "Substitution" = None,
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
            answer = tuple(
                result_sub.apply(v) for v in query.answer_variables
            )
            if answer not in seen:
                seen.add(answer)
                yield answer
