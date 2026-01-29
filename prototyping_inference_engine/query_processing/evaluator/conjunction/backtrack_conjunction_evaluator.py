"""
Backtracking-based conjunction evaluator.
"""
from typing import Iterator, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.query_processing.evaluator.conjunction.conjunction_evaluator import ConjunctionEvaluator
from prototyping_inference_engine.query_processing.evaluator.conjunction.scheduler.formula_scheduler import FormulaScheduler
from prototyping_inference_engine.query_processing.evaluator.conjunction.scheduler.formula_scheduler_provider import (
    FormulaSchedulerProvider,
    SequentialSchedulerProvider,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase
    from prototyping_inference_engine.query_processing.evaluator.formula_evaluator_registry import FormulaEvaluatorRegistry


class BacktrackConjunctionEvaluator(ConjunctionEvaluator):
    """
    Evaluates conjunction formulas using a backtracking algorithm.

    The evaluator flattens nested conjunctions and uses a scheduler to
    determine the order in which sub-formulas are evaluated. For each
    sub-formula, it delegates to the appropriate evaluator from the registry.

    Example:
        For formula (p(X,Y) ∧ q(Y)) ∧ r(X):
        1. Flatten to [p(X,Y), q(Y), r(X)]
        2. Evaluate p(X,Y) → yields {X→a, Y→b}
        3. Evaluate q(Y) with {X→a, Y→b} → yields {X→a, Y→b}
        4. Evaluate r(X) with {X→a, Y→b} → yields {X→a, Y→b}
        5. Final result: {X→a, Y→b}
    """

    def __init__(
        self,
        registry: Optional["FormulaEvaluatorRegistry"] = None,
        scheduler_provider: Optional[FormulaSchedulerProvider] = None,
    ):
        """
        Create a backtracking conjunction evaluator.

        Args:
            registry: The formula evaluator registry. If None, uses the singleton.
            scheduler_provider: Provider for formula schedulers.
                               Defaults to SequentialSchedulerProvider.
        """
        self._registry = registry
        self._scheduler_provider = scheduler_provider or SequentialSchedulerProvider()

    def _get_registry(self) -> "FormulaEvaluatorRegistry":
        """Get the registry, lazily importing if needed."""
        if self._registry is None:
            from prototyping_inference_engine.query_processing.evaluator.formula_evaluator_registry import (
                FormulaEvaluatorRegistry,
            )
            self._registry = FormulaEvaluatorRegistry.instance()
        return self._registry

    def evaluate(
        self,
        formula: ConjunctionFormula,
        fact_base: "FactBase",
        substitution: Substitution = None,
    ) -> Iterator[Substitution]:
        """
        Evaluate a conjunction formula against a fact base.

        Args:
            formula: The conjunction formula to evaluate
            fact_base: The fact base to query
            substitution: An optional initial substitution

        Yields:
            All substitutions that satisfy the conjunction
        """
        if substitution is None:
            substitution = Substitution()

        # Flatten the conjunction into a list of sub-formulas
        sub_formulas = self._flatten_conjunction(formula)

        # Create a scheduler for these formulas
        scheduler = self._scheduler_provider.create_scheduler(sub_formulas)

        # Run backtracking
        yield from self._backtrack(fact_base, substitution, scheduler, level=0)

    def _flatten_conjunction(self, formula: ConjunctionFormula) -> list[Formula]:
        """
        Flatten nested conjunctions into a list of sub-formulas.

        For (p ∧ q) ∧ r, returns [p, q, r].
        For p ∧ (q ∧ r), returns [p, q, r].
        For (p ∧ q) ∧ (r ∧ s), returns [p, q, r, s].
        """
        result: list[Formula] = []

        if isinstance(formula.left, ConjunctionFormula):
            result.extend(self._flatten_conjunction(formula.left))
        else:
            result.append(formula.left)

        if isinstance(formula.right, ConjunctionFormula):
            result.extend(self._flatten_conjunction(formula.right))
        else:
            result.append(formula.right)

        return result

    def _backtrack(
        self,
        fact_base: "FactBase",
        substitution: Substitution,
        scheduler: FormulaScheduler,
        level: int,
    ) -> Iterator[Substitution]:
        """
        Recursive backtracking algorithm.

        Args:
            fact_base: The fact base to query
            substitution: The current substitution
            scheduler: The formula scheduler
            level: The current backtracking level

        Yields:
            All substitutions that satisfy all remaining formulas
        """
        if not scheduler.has_next(level):
            # All sub-formulas have been satisfied
            yield substitution
        else:
            # Get the next formula to evaluate
            next_formula = scheduler.next_formula(substitution, level)

            # Get the appropriate evaluator for this formula type
            evaluator = self._get_registry().get_evaluator(next_formula)

            if evaluator is None:
                from prototyping_inference_engine.query_processing.evaluator.fo_query_evaluator import (
                    UnsupportedFormulaError,
                )
                raise UnsupportedFormulaError(type(next_formula))

            # Evaluate the formula and recurse for each result
            for extended_sub in evaluator.evaluate(next_formula, fact_base, substitution):
                yield from self._backtrack(fact_base, extended_sub, scheduler, level + 1)
