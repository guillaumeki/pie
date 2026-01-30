"""
Evaluator for negation formulas.
"""
import warnings
from itertools import product
from typing import Type, Iterator, TYPE_CHECKING, Optional

from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator import FormulaEvaluator

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import (
        FormulaEvaluatorRegistry,
    )


class UnsafeNegationWarning(UserWarning):
    """Warning emitted when evaluating unsafe negation (free variables in negated formula)."""
    pass


class NegationFormulaEvaluator(FormulaEvaluator[NegationFormula]):
    """
    Evaluator for negation formulas using negation-as-failure (NAF).

    For safe negation (all variables bound): returns the substitution if the
    inner formula has no results, otherwise returns nothing.

    For unsafe negation (free variables): iterates over the domain and returns
    all substitutions where the inner formula fails. Emits a warning.
    """

    def __init__(self, registry: Optional["FormulaEvaluatorRegistry"] = None):
        self._registry = registry

    def _get_registry(self) -> "FormulaEvaluatorRegistry":
        if self._registry is None:
            from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import (
                FormulaEvaluatorRegistry,
            )
            return FormulaEvaluatorRegistry.instance()
        return self._registry

    @classmethod
    def supported_formula_type(cls) -> Type[NegationFormula]:
        return NegationFormula

    def evaluate(
        self,
        formula: NegationFormula,
        fact_base: "FactBase",
        substitution: "Substitution" = None,
    ) -> Iterator["Substitution"]:
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        if substitution is None:
            substitution = Substitution()

        inner = formula.inner
        inner_free_vars = inner.free_variables
        bound_vars = set(substitution.domain)
        unbound_vars = inner_free_vars - bound_vars

        if not unbound_vars:
            # Safe negation: all variables are bound
            yield from self._evaluate_safe(inner, fact_base, substitution)
        else:
            # Unsafe negation: iterate over domain
            yield from self._evaluate_unsafe(
                inner, fact_base, substitution, unbound_vars
            )

    def _evaluate_safe(
        self,
        inner_formula,
        fact_base: "FactBase",
        substitution: "Substitution",
    ) -> Iterator["Substitution"]:
        """Evaluate safe negation using negation-as-failure."""
        inner_evaluator = self._get_registry().get_evaluator(inner_formula)
        if inner_evaluator is None:
            raise ValueError(f"No evaluator found for formula type: {type(inner_formula)}")

        # Check if inner formula has any results
        results = inner_evaluator.evaluate(inner_formula, fact_base, substitution)
        has_result = False
        for _ in results:
            has_result = True
            break

        # Negation succeeds if inner formula fails
        if not has_result:
            yield substitution

    def _evaluate_unsafe(
        self,
        inner_formula,
        fact_base: "FactBase",
        substitution: "Substitution",
        unbound_vars: set,
    ) -> Iterator["Substitution"]:
        """Evaluate unsafe negation by iterating over the domain."""
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        warnings.warn(
            f"Unsafe negation: variables {unbound_vars} are free in negated formula. "
            "Iterating over the entire domain. This may be slow for large fact bases.",
            UnsafeNegationWarning,
            stacklevel=4,
        )

        # Get the domain (all terms in the fact base)
        if not hasattr(fact_base, 'terms'):
            raise ValueError(
                "Cannot evaluate unsafe negation: fact base does not support "
                "term enumeration. Use a safe negation pattern instead."
            )

        domain = fact_base.terms
        if not domain:
            return

        unbound_vars_list = list(unbound_vars)
        inner_evaluator = self._get_registry().get_evaluator(inner_formula)
        if inner_evaluator is None:
            raise ValueError(f"No evaluator found for formula type: {type(inner_formula)}")

        # Iterate over all possible assignments for unbound variables
        for assignment in product(domain, repeat=len(unbound_vars_list)):
            # Create substitution for this assignment
            var_assignment = dict(zip(unbound_vars_list, assignment))
            extended_sub = substitution.compose(Substitution(var_assignment))

            # Check if inner formula has any results with this assignment
            results = inner_evaluator.evaluate(inner_formula, fact_base, extended_sub)
            has_result = False
            for _ in results:
                has_result = True
                break

            # Negation succeeds if inner formula fails
            if not has_result:
                yield extended_sub
