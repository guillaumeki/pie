"""
Evaluator for atomic formulas.
"""

from typing import Type, Iterator, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.registry.formula_evaluator import (
    FormulaEvaluator,
    RegistryMixin,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.prepared_queries import (
    prepare_atomic_or_conjunction,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData


class AtomEvaluator(RegistryMixin, FormulaEvaluator[Atom]):
    """
    Evaluates atomic formulas against a readable data source.

    For an atom p(X, Y) and a data source containing {p(a, b), p(a, c)},
    this evaluator yields substitutions {X -> a, Y -> b} and {X -> a, Y -> c}.

    The evaluator creates a BasicQuery from the atom and delegates evaluation
    to the data source. The data source returns tuples of terms for answer
    positions. The evaluator maps these to variables and handles post-filtering
    (e.g., when the same variable appears at multiple positions).
    """

    @classmethod
    def supported_formula_type(cls) -> Type[Atom]:
        return Atom

    def evaluate(
        self,
        formula: Atom,
        data: "ReadableData",
        substitution: Optional[Substitution] = None,
    ) -> Iterator[Substitution]:
        """
        Evaluate an atomic formula against a data source.

        Creates a BasicQuery from the atom with the current substitution,
        delegates to the data source, then maps results to substitutions.

        Args:
            formula: The atom to evaluate
            data: The data source to query
            substitution: An optional initial substitution

        Yields:
            All substitutions that map the atom to facts in the data source

        Raises:
            ValueError: If the atom cannot be evaluated (constraints not satisfied)
        """
        initial_sub = substitution if substitution is not None else Substitution()
        query = FOQuery(formula, sorted(formula.free_variables, key=lambda v: str(v)))
        prepared = prepare_atomic_or_conjunction(query, data)
        yield from prepared.execute(initial_sub)
