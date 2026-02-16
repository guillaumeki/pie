"""
Evaluator for ConjunctiveQuery.
"""

# References:
# - "Foundations of Databases" —
#   Serge Abiteboul, Richard Hull, Victor Vianu.
#   Link: https://dl.acm.org/doi/book/10.5555/64510
#
# Summary:
# Conjunctive query answering reduces to finding homomorphisms from the query
# body to the database instance.
#
# Properties used here:
# - Correctness of CQ evaluation via homomorphisms.
#
# Implementation notes:
# This evaluator delegates CQ evaluation to the FO query evaluator stack.

from typing import Iterator, Type, Optional, TYPE_CHECKING, cast, Iterable

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator import (
    QueryEvaluator,
)
from prototyping_inference_engine.api.query.prepared_query import PreparedQuery

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.query.fo_query import FOQuery
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
        prepared = self.prepare(query, data)
        from prototyping_inference_engine.api.substitution.substitution import (
            Substitution,
        )

        initial = substitution if substitution is not None else Substitution()
        yield from prepared.execute(initial)

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

    def prepare(
        self,
        query: ConjunctiveQuery,
        data: "ReadableData",
    ) -> "PreparedQuery[ConjunctiveQuery, ReadableData, Iterable[Substitution], Substitution]":
        fo_query = query.to_fo_query()
        registry = self._get_registry()
        evaluator = registry.get_evaluator(fo_query)

        if evaluator is None:
            raise ValueError("No evaluator registered for FOQuery")

        prepared = evaluator.prepare(fo_query, data)
        return _DelegatingPreparedQuery(query, data, prepared)


class _DelegatingPreparedQuery(
    PreparedQuery[
        ConjunctiveQuery, "ReadableData", Iterable["Substitution"], "Substitution"
    ]
):
    def __init__(
        self,
        query: ConjunctiveQuery,
        data: "ReadableData",
        delegate: "PreparedQuery[FOQuery, ReadableData, Iterable[Substitution], Substitution]",
    ):
        self._query = query
        self._data = data
        self._delegate = delegate

    @property
    def query(self) -> ConjunctiveQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._data

    def execute(self, assignation: "Substitution") -> Iterable["Substitution"]:
        return self._delegate.execute(assignation)

    def estimate_bound(self, assignation: "Substitution") -> int | None:
        return self._delegate.estimate_bound(assignation)
