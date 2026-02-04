"""
Evaluator for atomic formulas.
"""
from typing import Type, Iterator, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator import FormulaEvaluator
from prototyping_inference_engine.query_evaluation.evaluator.function_term_rewriter import (
    formula_contains_function,
    rewrite_atom_function_terms,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData


class AtomEvaluator(FormulaEvaluator[Atom]):
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
        substitution: Substitution = None,
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

        if formula_contains_function(formula):
            atoms = rewrite_atom_function_terms(formula)
            if len(atoms) > 1:
                from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
                from prototyping_inference_engine.query_evaluation.evaluator.conjunction.backtrack_conjunction_evaluator import (
                    BacktrackConjunctionEvaluator,
                )

                conjunction = _build_conjunction(atoms)
                evaluator = BacktrackConjunctionEvaluator()
                yield from evaluator.evaluate(conjunction, data, initial_sub)
                return

        # Create a BasicQuery from the atom
        query = BasicQuery.from_atom(formula, initial_sub)

        # Check if the data source can evaluate this query
        if not data.can_evaluate(query):
            pattern = data.get_atomic_pattern(formula.predicate)
            unsatisfied = pattern.get_unsatisfied_positions(formula, initial_sub)
            raise ValueError(
                f"Cannot evaluate atom {formula}: "
                f"unsatisfied constraints at positions {unsatisfied}"
            )

        # Get answer positions in sorted order (matches tuple order from data source)
        answer_positions = sorted(query.answer_variables.keys())

        # Evaluate and map results to substitutions
        for term_tuple in data.evaluate(query):
            # Map tuple values to variables
            result = {}
            consistent = True

            for pos, term in zip(answer_positions, term_tuple):
                var = query.answer_variables[pos]
                if var in result:
                    # Same variable at multiple positions: check consistency
                    if result[var] != term:
                        consistent = False
                        break
                else:
                    result[var] = term

            if consistent:
                yield initial_sub.compose(Substitution(result))


def _build_conjunction(formulas: list[Atom]) -> "ConjunctionFormula":
    from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula

    if not formulas:
        raise ValueError("Cannot build conjunction from empty formula list.")

    current = formulas[0]
    for next_formula in formulas[1:]:
        current = ConjunctionFormula(current, next_formula)
    return current
