"""
Abstract base class for conjunction evaluators.
"""
from abc import ABC
from typing import Type

from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.query_evaluation.evaluator.registry.formula_evaluator import FormulaEvaluator


class ConjunctionEvaluator(FormulaEvaluator[ConjunctionFormula], ABC):
    """
    Abstract base class for evaluating conjunction formulas.

    This class provides the extension point for different conjunction
    evaluation strategies (backtracking, join-based, etc.).
    """

    @classmethod
    def supported_formula_type(cls) -> Type[ConjunctionFormula]:
        return ConjunctionFormula
