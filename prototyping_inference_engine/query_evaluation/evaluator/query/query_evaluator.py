"""
Abstract base class for query evaluators.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Iterator, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.query.query import Query

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.substitution.substitution import Substitution

Q = TypeVar("Q", bound=Query)


class QueryEvaluator(ABC, Generic[Q]):
    """
    Abstract base class for query evaluators.

    Each concrete evaluator handles a specific type of query and yields
    substitutions that satisfy the query.
    """

    @classmethod
    @abstractmethod
    def supported_query_type(cls) -> Type[Q]:
        """Return the query type this evaluator handles."""
        ...

    @abstractmethod
    def evaluate(
        self,
        query: Q,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        """
        Evaluate a query against a data source.

        Args:
            query: The query to evaluate
            data: The data source to query
            substitution: An optional initial substitution (pre-homomorphism)

        Yields:
            Substitutions that satisfy the query
        """
        ...
