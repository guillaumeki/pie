"""
Evaluator for disjunction formulas.
"""
from typing import Type, Iterator, TYPE_CHECKING, Optional

from prototyping_inference_engine.api.formula.disjunction_formula import DisjunctionFormula
from prototyping_inference_engine.query_evaluation.evaluator.registry.formula_evaluator import (
    FormulaEvaluator,
    RegistryMixin,
)

from prototyping_inference_engine.query_evaluation.evaluator.errors import UnsupportedFormulaError

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.registry.formula_evaluator_registry import (
        FormulaEvaluatorRegistry,
    )


class DisjunctionFormulaEvaluator(RegistryMixin, FormulaEvaluator[DisjunctionFormula]):
    """
    Evaluator for disjunction formulas (φ ∨ ψ).

    A disjunction is satisfied if at least one of the sub-formulas is satisfied.
    Returns the union of results from both sub-formulas, deduplicated.
    """

    def __init__(self, registry: Optional["FormulaEvaluatorRegistry"] = None):
        RegistryMixin.__init__(self, registry)

    @classmethod
    def supported_formula_type(cls) -> Type[DisjunctionFormula]:
        return DisjunctionFormula

    def evaluate(
        self,
        formula: DisjunctionFormula,
        data: "ReadableData",
        substitution: "Substitution" = None,
    ) -> Iterator["Substitution"]:
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        if substitution is None:
            substitution = Substitution()

        registry = self._get_registry()

        # Get evaluators for both sub-formulas
        left_evaluator = registry.get_evaluator(formula.left)
        if left_evaluator is None:
            raise UnsupportedFormulaError(type(formula.left))

        right_evaluator = registry.get_evaluator(formula.right)
        if right_evaluator is None:
            raise UnsupportedFormulaError(type(formula.right))

        # Track seen results for deduplication
        seen = set()

        # Evaluate left sub-formula
        for result_sub in left_evaluator.evaluate(formula.left, data, substitution):
            key = frozenset(result_sub.items())
            if key not in seen:
                seen.add(key)
                yield result_sub

        # Evaluate right sub-formula
        for result_sub in right_evaluator.evaluate(formula.right, data, substitution):
            key = frozenset(result_sub.items())
            if key not in seen:
                seen.add(key)
                yield result_sub
