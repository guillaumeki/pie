"""
Protocol and providers for formula schedulers.
"""
from typing import Protocol, runtime_checkable

from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.query_processing.evaluator.conjunction.scheduler.formula_scheduler import FormulaScheduler


@runtime_checkable
class FormulaSchedulerProvider(Protocol):
    """Protocol for providing a FormulaScheduler."""

    def create_scheduler(self, formulas: list[Formula]) -> FormulaScheduler:
        """
        Create a scheduler for the given formulas.

        Args:
            formulas: The list of sub-formulas to schedule

        Returns:
            A FormulaScheduler instance
        """
        ...


class SequentialSchedulerProvider:
    """Provides SequentialFormulaScheduler instances."""

    def create_scheduler(self, formulas: list[Formula]) -> FormulaScheduler:
        from prototyping_inference_engine.query_processing.evaluator.conjunction.scheduler.sequential_formula_scheduler import (
            SequentialFormulaScheduler,
        )
        return SequentialFormulaScheduler(formulas)
