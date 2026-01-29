"""
Registry for formula evaluators.
"""
from typing import Type, Optional

from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.query.evaluator.formula_evaluator import FormulaEvaluator


class FormulaEvaluatorRegistry:
    """
    Singleton registry for formula evaluators.

    Allows registering new evaluators for different formula types,
    supporting the Open/Closed Principle - new formula types can be
    added by registering new evaluators without modifying existing code.

    Example:
        # Register a new evaluator
        FormulaEvaluatorRegistry.instance().register(ConjunctionEvaluator())

        # Get evaluator for a formula
        evaluator = FormulaEvaluatorRegistry.instance().get_evaluator(my_formula)
    """

    _instance: Optional["FormulaEvaluatorRegistry"] = None

    def __init__(self):
        self._evaluators: dict[Type[Formula], FormulaEvaluator] = {}

    @classmethod
    def instance(cls) -> "FormulaEvaluatorRegistry":
        """
        Get the singleton instance, creating it if necessary.

        The instance is initialized with the default AtomEvaluator.
        """
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
        from prototyping_inference_engine.api.query.evaluator.atom_evaluator import AtomEvaluator
        from prototyping_inference_engine.api.query.evaluator.conjunction.backtrack_conjunction_evaluator import (
            BacktrackConjunctionEvaluator,
        )
        self.register(AtomEvaluator())
        self.register(BacktrackConjunctionEvaluator(registry=self))

    def register(self, evaluator: FormulaEvaluator) -> None:
        """
        Register an evaluator for a formula type.

        Args:
            evaluator: The evaluator to register
        """
        self._evaluators[evaluator.supported_formula_type()] = evaluator

    def get_evaluator(self, formula: Formula) -> Optional[FormulaEvaluator]:
        """
        Get the evaluator for a formula.

        Args:
            formula: The formula to find an evaluator for

        Returns:
            The evaluator for this formula type, or None if not found
        """
        formula_type = type(formula)

        # Try exact match first
        if formula_type in self._evaluators:
            return self._evaluators[formula_type]

        # Try subclass match
        for registered_type, evaluator in self._evaluators.items():
            if isinstance(formula, registered_type):
                return evaluator

        return None

    def supported_formula_types(self) -> tuple[Type[Formula], ...]:
        """Return all registered formula types."""
        return tuple(self._evaluators.keys())
