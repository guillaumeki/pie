"""
Evaluator for existential quantification formulas.
"""
from typing import Type, Iterator, TYPE_CHECKING, Optional

from prototyping_inference_engine.api.formula.existential_formula import ExistentialFormula
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator import (
    FormulaEvaluator,
    RegistryMixin,
)

from prototyping_inference_engine.query_evaluation.evaluator.fo_query_evaluator import (
    UnsupportedFormulaError,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import (
        FormulaEvaluatorRegistry,
    )


class ExistentialFormulaEvaluator(RegistryMixin, FormulaEvaluator[ExistentialFormula]):
    """
    Evaluator for existential quantification formulas (∃x.φ).

    For ∃x.φ(x) to be satisfied, φ must hold for AT LEAST ONE term.
    The bound variable x is projected out of the results.

    This is efficient: we simply evaluate φ with x as a free variable,
    then remove x from the resulting substitutions and deduplicate.
    """

    def __init__(self, registry: Optional["FormulaEvaluatorRegistry"] = None):
        RegistryMixin.__init__(self, registry)

    @classmethod
    def supported_formula_type(cls) -> Type[ExistentialFormula]:
        return ExistentialFormula

    def evaluate(
        self,
        formula: ExistentialFormula,
        fact_base: "FactBase",
        substitution: "Substitution" = None,
    ) -> Iterator["Substitution"]:
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        if substitution is None:
            substitution = Substitution()

        inner = formula.inner
        bound_var = formula.variable

        inner_evaluator = self._get_registry().get_evaluator(inner)
        if inner_evaluator is None:
            raise UnsupportedFormulaError(type(inner))

        # Track seen results for deduplication
        seen = set()

        # Evaluate inner formula (bound variable is treated as free)
        for result_sub in inner_evaluator.evaluate(inner, fact_base, substitution):
            # Project out the bound variable
            projected = Substitution({
                k: v for k, v in result_sub.items() if k != bound_var
            })

            # Deduplicate
            key = frozenset(projected.items())
            if key not in seen:
                seen.add(key)
                yield projected
