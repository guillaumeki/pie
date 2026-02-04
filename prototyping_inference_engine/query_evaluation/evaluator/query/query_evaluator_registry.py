"""
Registry for query evaluators.
"""

from typing import Type, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator import (
    QueryEvaluator,
)

if TYPE_CHECKING:
    pass


class QueryEvaluatorRegistry:
    """
    Singleton registry for query evaluators.

    Maps query types to their corresponding QueryEvaluator implementations.
    This is a general registry that can handle any query type (FOQuery,
    UnionQuery, ConjunctiveQuery, etc.).
    """

    _instance: Optional["QueryEvaluatorRegistry"] = None

    def __init__(self):
        self._evaluators: dict[Type[Query], QueryEvaluator] = {}

    @classmethod
    def instance(cls) -> "QueryEvaluatorRegistry":
        """Get the singleton instance, creating it if necessary."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._register_defaults()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None

    def _register_defaults(self) -> None:
        """Register default evaluators."""
        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
            GenericFOQueryEvaluator,
        )
        from prototyping_inference_engine.query_evaluation.evaluator.query.union_query_evaluator import (
            UnionQueryEvaluator,
        )
        from prototyping_inference_engine.query_evaluation.evaluator.query.conjunctive_query_evaluator import (
            ConjunctiveQueryEvaluator,
        )

        # Register FOQuery evaluator (delegates to formula-based registry)
        self.register(GenericFOQueryEvaluator())

        # Register UnionQuery evaluator
        self.register(UnionQueryEvaluator(self))

        # Register ConjunctiveQuery evaluator (converts to FOQuery)
        self.register(ConjunctiveQueryEvaluator(self))

    def register(self, evaluator: QueryEvaluator) -> None:
        """Register an evaluator for a query type."""
        self._evaluators[evaluator.supported_query_type()] = evaluator

    def get_evaluator(self, query: Query) -> Optional[QueryEvaluator]:
        """
        Get the evaluator for a query based on its type.

        Args:
            query: The query to find an evaluator for

        Returns:
            The evaluator for this query type, or None if not found
        """
        query_type = type(query)

        # Try exact match first
        if query_type in self._evaluators:
            return self._evaluators[query_type]

        # Try subclass match
        for registered_type, evaluator in self._evaluators.items():
            if isinstance(query, registered_type):
                return evaluator

        return None

    def supported_query_types(self) -> tuple[Type[Query], ...]:
        """Return all registered query types."""
        return tuple(self._evaluators.keys())
