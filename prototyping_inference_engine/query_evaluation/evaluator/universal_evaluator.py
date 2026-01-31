"""
Evaluator for universal quantification formulas.
"""
import warnings
from typing import Type, Iterator, TYPE_CHECKING, Optional

from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator import (
    FormulaEvaluator,
    RegistryMixin,
)

from prototyping_inference_engine.query_evaluation.evaluator.fo_query_evaluator import (
    UnsupportedFormulaError,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import (
        FormulaEvaluatorRegistry,
    )


class UniversalQuantifierWarning(UserWarning):
    """Warning emitted when evaluating universal quantifier (requires domain iteration)."""
    pass


class UniversalFormulaEvaluator(RegistryMixin, FormulaEvaluator[UniversalFormula]):
    """
    Evaluator for universal quantification formulas (∀x.φ).

    For ∀x.φ(x) to be satisfied, φ must hold for ALL terms in the domain.
    This requires iterating over the entire domain, which emits a warning.

    If φ has additional free variables Y, returns substitutions for Y
    such that φ(x, Y) holds for ALL x in the domain (intersection semantics).
    """

    def __init__(self, registry: Optional["FormulaEvaluatorRegistry"] = None):
        RegistryMixin.__init__(self, registry)

    @classmethod
    def supported_formula_type(cls) -> Type[UniversalFormula]:
        return UniversalFormula

    def evaluate(
        self,
        formula: UniversalFormula,
        data: "ReadableData",
        substitution: "Substitution" = None,
    ) -> Iterator["Substitution"]:
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        if substitution is None:
            substitution = Substitution()

        # Get the domain
        if not hasattr(data, 'terms'):
            raise ValueError(
                "Cannot evaluate universal quantifier: data source does not support "
                "term enumeration."
            )

        domain = data.terms
        if not domain:
            # Empty domain: ∀x.φ is vacuously true
            yield substitution
            return

        warnings.warn(
            f"Universal quantifier ∀{formula.variable}: iterating over domain "
            f"({len(domain)} terms). This may be slow for large data sources.",
            UniversalQuantifierWarning,
            stacklevel=3,
        )

        inner = formula.inner
        bound_var = formula.variable
        inner_evaluator = self._get_registry().get_evaluator(inner)
        if inner_evaluator is None:
            raise UnsupportedFormulaError(type(inner))

        # Check if there are other free variables (besides the bound one)
        other_free_vars = formula.free_variables  # Already excludes bound_var
        has_other_free_vars = bool(other_free_vars - substitution.domain)

        if not has_other_free_vars:
            # Simple case: just check if φ holds for all x
            yield from self._evaluate_boolean(
                inner, data, substitution, bound_var, domain, inner_evaluator
            )
        else:
            # Complex case: find intersection of results across all x values
            yield from self._evaluate_with_free_vars(
                inner, data, substitution, bound_var, domain, inner_evaluator
            )

    def _evaluate_boolean(
        self,
        inner_formula,
        data: "ReadableData",
        substitution: "Substitution",
        bound_var,
        domain,
        inner_evaluator,
    ) -> Iterator["Substitution"]:
        """Evaluate ∀x.φ where φ has no other free variables."""
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        for term in domain:
            extended_sub = substitution.compose(Substitution({bound_var: term}))

            # Check if inner formula has at least one result
            has_result = False
            for _ in inner_evaluator.evaluate(inner_formula, data, extended_sub):
                has_result = True
                break

            if not has_result:
                # Found a counterexample: φ(term) is false
                return

        # All terms satisfied φ
        yield substitution

    def _evaluate_with_free_vars(
        self,
        inner_formula,
        data: "ReadableData",
        substitution: "Substitution",
        bound_var,
        domain,
        inner_evaluator,
    ) -> Iterator["Substitution"]:
        """Evaluate ∀x.φ(x, Y) where Y are additional free variables.

        Returns substitutions for Y such that φ(x, Y) holds for ALL x.
        Uses intersection semantics.
        """
        from prototyping_inference_engine.api.substitution.substitution import Substitution

        # For the first term, get all possible results
        first_term = True
        valid_subs = None  # Will hold set of valid substitution tuples

        for term in domain:
            extended_sub = substitution.compose(Substitution({bound_var: term}))

            # Get all results for this term
            results = set()
            for result_sub in inner_evaluator.evaluate(inner_formula, data, extended_sub):
                # Remove the bound variable from the result
                filtered = Substitution({
                    k: v for k, v in result_sub.items() if k != bound_var
                })
                # Convert to hashable tuple for set operations
                results.add(tuple(sorted(filtered.items())))

            if first_term:
                valid_subs = results
                first_term = False
            else:
                # Intersection: keep only results that appear for ALL terms
                valid_subs = valid_subs & results

            # Early termination if intersection is empty
            if not valid_subs:
                return

        # Convert back to substitutions and yield
        if valid_subs:
            for sub_tuple in valid_subs:
                yield Substitution(dict(sub_tuple))
