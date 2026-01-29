"""
Evaluator for first-order queries.
"""
from typing import Iterator, Tuple, TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import FormulaEvaluatorRegistry
from prototyping_inference_engine.api.query.fo_query import FOQuery

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase


class UnsupportedFormulaError(Exception):
    """Raised when no evaluator is registered for a formula type."""

    def __init__(self, formula_type: type):
        self.formula_type = formula_type
        super().__init__(
            f"No evaluator registered for formula type: {formula_type.__name__}"
        )


class FOQueryEvaluator:
    """
    Evaluates first-order queries against a fact base.

    Uses the FormulaEvaluatorRegistry to dispatch evaluation to the
    appropriate evaluator based on the formula type.

    Example:
        evaluator = FOQueryEvaluator()
        for answer in evaluator.evaluate(query, fact_base):
            print(answer)  # Tuple of terms for answer variables
    """

    def __init__(self, registry: FormulaEvaluatorRegistry = None):
        """
        Create a query evaluator.

        Args:
            registry: The formula evaluator registry to use.
                      Defaults to the singleton instance.
        """
        self._registry = registry or FormulaEvaluatorRegistry.instance()

    def evaluate(
        self,
        query: FOQuery,
        fact_base: "FactBase",
    ) -> Iterator[Tuple[Term, ...]]:
        """
        Evaluate a query against a fact base.

        Args:
            query: The first-order query to evaluate
            fact_base: The fact base to query

        Yields:
            Tuples of terms corresponding to the answer variables

        Raises:
            UnsupportedFormulaError: If no evaluator is registered for
                                     the query's formula type
        """
        formula = query.formula
        evaluator = self._registry.get_evaluator(formula)

        if evaluator is None:
            raise UnsupportedFormulaError(type(formula))

        seen: set[Tuple[Term, ...]] = set()

        for substitution in evaluator.evaluate(formula, fact_base):
            # Project the substitution onto the answer variables
            answer = tuple(
                substitution.apply(v) for v in query.answer_variables
            )

            # Deduplicate answers
            if answer not in seen:
                seen.add(answer)
                yield answer
