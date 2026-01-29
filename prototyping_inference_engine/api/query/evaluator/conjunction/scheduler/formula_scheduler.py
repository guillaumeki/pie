"""
Abstract base class for formula schedulers.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.formula.formula import Formula

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class FormulaScheduler(ABC):
    """
    Strategy for ordering formula evaluation in backtracking.

    The scheduler determines the order in which sub-formulas are evaluated
    during conjunction evaluation. Different schedulers can implement different
    ordering strategies for optimization.
    """

    def __init__(self, formulas: list[Formula]):
        """
        Initialize the scheduler with the formulas to schedule.

        Args:
            formulas: The list of sub-formulas to schedule
        """
        self._formulas = formulas

    @property
    def formulas(self) -> list[Formula]:
        """The formulas being scheduled."""
        return self._formulas

    @abstractmethod
    def has_next(self, level: int) -> bool:
        """
        Check if there is a next formula at the given backtracking level.

        Args:
            level: The current backtracking level (0-indexed)

        Returns:
            True if there is a formula to evaluate at this level
        """
        pass

    @abstractmethod
    def next_formula(self, substitution: "Substitution", level: int) -> Formula:
        """
        Get the next formula to evaluate at the given level.

        Args:
            substitution: The current substitution
            level: The current backtracking level

        Returns:
            The next formula to evaluate
        """
        pass
