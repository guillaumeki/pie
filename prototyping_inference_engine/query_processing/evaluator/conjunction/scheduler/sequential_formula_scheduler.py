"""
Sequential formula scheduler - evaluates formulas in order.
"""
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.query_processing.evaluator.conjunction.scheduler.formula_scheduler import FormulaScheduler

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class SequentialFormulaScheduler(FormulaScheduler):
    """
    Evaluates sub-formulas in sequential order (left to right).

    This is the simplest scheduling strategy - formulas are evaluated
    in the order they appear in the conjunction.
    """

    def has_next(self, level: int) -> bool:
        """Check if there is a formula at the given level."""
        return level < len(self._formulas)

    def next_formula(self, substitution: "Substitution", level: int) -> Formula:
        """
        Get the formula at the given level.

        The substitution is ignored in sequential scheduling.
        """
        return self._formulas[level]
