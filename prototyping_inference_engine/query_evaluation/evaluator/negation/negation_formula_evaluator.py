"""
Evaluator for negation formulas.
"""
import warnings
from itertools import product
from typing import Type, Iterator, TYPE_CHECKING, Optional

from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
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


class UnsafeNegationWarning(UserWarning):
    """Warning emitted when evaluating unsafe negation (free variables in negated formula)."""
    pass


class NegationFormulaEvaluator(RegistryMixin, FormulaEvaluator[NegationFormula]):
    """
    Evaluator for negation formulas using negation-as-failure (NAF).

    For safe negation (all variables bound): returns the substitution if the
    inner formula has no results, otherwise returns nothing.

    For unsafe negation (free variables): iterates over the domain and returns
    all substitutions where the inner formula fails. Emits a warning.
    """

    def __init__(self, registry: Optional["FormulaEvaluatorRegistry"] = None):
        RegistryMixin.__init__(self, registry)

    @classmethod
    def supported_formula_type(cls) -> Type[NegationFormula]:
        return NegationFormula

    def evaluate(
        self,
        formula: NegationFormula,
        data: "ReadableData",
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
            yield from self._evaluate_safe(inner, data, substitution)
        else:
            # Unsafe negation: iterate over domain
            yield from self._evaluate_unsafe(
                inner, data, substitution, unbound_vars
            )

    def _evaluate_safe(
        self,
        inner_formula,
        data: "ReadableData",
        substitution: "Substitution",
    ) -> Iterator["Substitution"]:
        """Evaluate safe negation using negation-as-failure."""
        inner_evaluator = self._get_registry().get_evaluator(inner_formula)
        if inner_evaluator is None:
            raise UnsupportedFormulaError(type(inner_formula))

        # Check if inner formula has any results
        results = inner_evaluator.evaluate(inner_formula, data, substitution)
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
        data: "ReadableData",
        substitution: "Substitution",
        unbound_vars: set,
    ) -> Iterator["Substitution"]:
        """Evaluate unsafe negation by iterating over the domain."""
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        warnings.warn(
            f"Unsafe negation: variables {unbound_vars} are free in negated formula. "
            "Iterating over the entire domain. This may be slow for large data sources.",
            UnsafeNegationWarning,
            stacklevel=4,
        )

        # Get the domain (all terms in the data source)
        if not hasattr(data, 'terms'):
            raise ValueError(
                "Cannot evaluate unsafe negation: data source does not support "
                "term enumeration. Use a safe negation pattern instead."
            )

        domain = data.terms
        if not domain:
            return

        unbound_vars_list = list(unbound_vars)
        inner_evaluator = self._get_registry().get_evaluator(inner_formula)
        if inner_evaluator is None:
            raise UnsupportedFormulaError(type(inner_formula))

        # Iterate over all possible assignments for unbound variables
        for assignment in product(domain, repeat=len(unbound_vars_list)):
            # Create substitution for this assignment
            var_assignment = dict(zip(unbound_vars_list, assignment))
            extended_sub = substitution.compose(Substitution(var_assignment))

            # Check if inner formula has any results with this assignment
            results = inner_evaluator.evaluate(inner_formula, data, extended_sub)
            has_result = False
            for _ in results:
                has_result = True
                break

            # Negation succeeds if inner formula fails
            if not has_result:
                yield extended_sub
