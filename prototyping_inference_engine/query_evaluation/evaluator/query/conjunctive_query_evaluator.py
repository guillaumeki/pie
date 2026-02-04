"""
Evaluator for ConjunctiveQuery.
"""

from typing import Iterator, Type, Optional, TYPE_CHECKING, cast

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator import (
    QueryEvaluator,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator_registry import (
        QueryEvaluatorRegistry,
    )


class ConjunctiveQueryEvaluator(QueryEvaluator[ConjunctiveQuery]):
    """
    Evaluator for ConjunctiveQuery.

    This evaluator converts the ConjunctiveQuery to a FOQuery and then
    delegates evaluation to the FOQuery evaluator via the registry.
    """

    def __init__(self, registry: Optional["QueryEvaluatorRegistry"] = None):
        """
        Create a ConjunctiveQueryEvaluator.

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
    def supported_query_type(cls) -> Type[ConjunctiveQuery]:
        return ConjunctiveQuery

    def evaluate(
        self,
        query: ConjunctiveQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        """
        Evaluate a ConjunctiveQuery against a data source.

        Converts the CQ to a FOQuery and delegates to the FOQuery evaluator.

        Args:
            query: The ConjunctiveQuery to evaluate
            data: The data source to query
            substitution: An optional initial substitution

        Yields:
            Substitutions that satisfy the query
        """
        fo_query = query.to_fo_query()
        registry = self._get_registry()
        evaluator = registry.get_evaluator(fo_query)

        if evaluator is None:
            raise ValueError("No evaluator registered for FOQuery")

        yield from evaluator.evaluate(fo_query, data, substitution)

    def evaluate_and_project(
        self,
        query: ConjunctiveQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator[tuple[Term, ...]]:
        """
        Evaluate a ConjunctiveQuery and project results onto answer variables.

        Args:
            query: The ConjunctiveQuery to evaluate
            data: The data source to query
            substitution: An optional initial substitution

        Yields:
            Tuples of terms for answer variables
        """
        fo_query = query.to_fo_query()
        registry = self._get_registry()
        evaluator = registry.get_evaluator(fo_query)

        if evaluator is None:
            raise ValueError("No evaluator registered for FOQuery")

        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator import (
            FOQueryEvaluator,
        )

        yield from cast(FOQueryEvaluator, evaluator).evaluate_and_project(
            fo_query, data, substitution
        )
