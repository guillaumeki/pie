"""
Abstract base class for formula evaluators.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Iterator, TYPE_CHECKING

from prototyping_inference_engine.api.formula.formula import Formula

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase
    from prototyping_inference_engine.api.substitution.substitution import Substitution

F = TypeVar("F", bound=Formula)


class FormulaEvaluator(ABC, Generic[F]):
    """
    Strategy for evaluating a specific type of formula against a fact base.

    Each concrete evaluator handles one formula type (Atom, Conjunction, etc.)
    and yields all substitutions that make the formula true in the fact base.
    """

    @classmethod
    @abstractmethod
    def supported_formula_type(cls) -> Type[F]:
        """Return the formula type this evaluator handles."""
        ...

    @abstractmethod
    def evaluate(
        self,
        formula: F,
        fact_base: "FactBase",
        substitution: "Substitution" = None,
    ) -> Iterator["Substitution"]:
        """
        Evaluate a formula against a fact base.

        Args:
            formula: The formula to evaluate
            fact_base: The fact base to query
            substitution: An optional initial substitution to apply

        Yields:
            All substitutions that satisfy the formula in the fact base
        """
        ...
