"""
Abstract base class for query evaluators.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Iterator, TYPE_CHECKING

from prototyping_inference_engine.api.query.query import Query

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase
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
        fact_base: "FactBase",
        substitution: "Substitution" = None,
    ) -> Iterator["Substitution"]:
        """
        Evaluate a query against a fact base.

        Args:
            query: The query to evaluate
            fact_base: The fact base to query
            substitution: An optional initial substitution (pre-homomorphism)

        Yields:
            Substitutions that satisfy the query
        """
        ...
