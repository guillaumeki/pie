"""
Backtracking-based conjunction evaluator.
"""

from typing import Iterator, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.query_evaluation.evaluator.conjunction.conjunction_evaluator import (
    ConjunctionEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.registry.formula_evaluator import (
    RegistryMixin,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.prepared_queries import (
    PreparedConjunctiveFOQuery,
)
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.query_evaluation.evaluator.registry.formula_evaluator_registry import (
        FormulaEvaluatorRegistry,
    )


class BacktrackConjunctionEvaluator(RegistryMixin, ConjunctionEvaluator):
    """
    Evaluates conjunction formulas using a backtracking algorithm.

    The evaluator prepares the conjunction once and uses a dynamic scheduler
    to order sub-formulas during backtracking.

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
        scheduler_provider: Optional[object] = None,
    ):
        """
        Create a backtracking conjunction evaluator.

        Args:
            registry: The formula evaluator registry. If None, uses the singleton.
            scheduler_provider: Reserved for future customization.
        """
        RegistryMixin.__init__(self, registry)
        self._scheduler_provider = scheduler_provider

    def evaluate(
        self,
        formula: ConjunctionFormula,
        data: "ReadableData",
        substitution: Optional[Substitution] = None,
    ) -> Iterator[Substitution]:
        """
        Evaluate a conjunction formula against a data source.

        Equality atoms (X = Y) are extracted and transformed into a TermPartition
        to handle transitive equalities correctly. The associated substitution
        is computed and applied before evaluating non-equality atoms.

        Args:
            formula: The conjunction formula to evaluate
            data: The data source to query
            substitution: An optional initial substitution

        Yields:
            All substitutions that satisfy the conjunction
        """
        if substitution is None:
            substitution = Substitution()

        prepared = PreparedConjunctiveFOQuery(
            FOQuery(formula, sorted(formula.free_variables, key=lambda v: str(v))),
            data,
        )
        yield from prepared.execute(substitution)
