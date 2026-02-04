"""
Registry for FOQuery evaluators.
"""

from typing import Type, Optional

from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator import (
    FOQueryEvaluator,
)


class FOQueryEvaluatorRegistry:
    """
    Singleton registry for FOQuery evaluators.

    Maps formula types to their corresponding FOQueryEvaluator implementations.
    """

    _instance: Optional["FOQueryEvaluatorRegistry"] = None

    def __init__(self):
        self._evaluators: dict[Type[Formula], FOQueryEvaluator] = {}

    @classmethod
    def instance(cls) -> "FOQueryEvaluatorRegistry":
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
            AtomicFOQueryEvaluator,
            ConjunctiveFOQueryEvaluator,
            DisjunctiveFOQueryEvaluator,
            NegationFOQueryEvaluator,
            UniversalFOQueryEvaluator,
            ExistentialFOQueryEvaluator,
        )

        self.register(AtomicFOQueryEvaluator())
        self.register(ConjunctiveFOQueryEvaluator(registry=self))
        self.register(DisjunctiveFOQueryEvaluator(registry=self))
        self.register(NegationFOQueryEvaluator(registry=self))
        self.register(UniversalFOQueryEvaluator(registry=self))
        self.register(ExistentialFOQueryEvaluator(registry=self))

    def register(self, evaluator: FOQueryEvaluator) -> None:
        """Register an evaluator for a formula type."""
        self._evaluators[evaluator.supported_formula_type()] = evaluator

    def get_evaluator(self, query: FOQuery) -> Optional[FOQueryEvaluator]:
        """
        Get the evaluator for a query based on its formula type.

        Args:
            query: The query to find an evaluator for

        Returns:
            The evaluator for this query's formula type, or None if not found
        """
        formula_type = type(query.formula)

        # Try exact match first
        if formula_type in self._evaluators:
            return self._evaluators[formula_type]

        # Try subclass match
        for registered_type, evaluator in self._evaluators.items():
            if isinstance(query.formula, registered_type):
                return evaluator

        return None

    def supported_formula_types(self) -> tuple[Type[Formula], ...]:
        """Return all registered formula types."""
        return tuple(self._evaluators.keys())
