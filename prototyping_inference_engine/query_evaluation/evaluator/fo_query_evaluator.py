"""
Abstract base class for first-order query evaluators.
"""
from abc import abstractmethod
from typing import Iterator, Tuple, Type, TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.query_evaluator import QueryEvaluator

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class UnsupportedFormulaError(Exception):
    """Raised when no evaluator is registered for a formula type."""

    def __init__(self, formula_type: type):
        self.formula_type = formula_type
        super().__init__(
            f"No evaluator registered for formula type: {formula_type.__name__}"
        )


class FOQueryEvaluator(QueryEvaluator[FOQuery]):
    """
    Abstract base class for first-order query evaluators.

    Each concrete evaluator handles FOQuery instances with a specific
    formula type (Atom, Conjunction, Disjunction, etc.).

    Type parameter F specifies the formula type this evaluator handles.
    Evaluators return Iterator[Substitution] - the projection to answer
    variable tuples is done separately.
    """

    @classmethod
    def supported_query_type(cls) -> Type[FOQuery]:
        return FOQuery

    @classmethod
    @abstractmethod
    def supported_formula_type(cls) -> Type[Formula]:
        """Return the formula type this evaluator handles."""
        ...

    @abstractmethod
    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: "Substitution" = None,
    ) -> Iterator["Substitution"]:
        """
        Evaluate a query against a data source.

        Args:
            query: The first-order query to evaluate
            data: The data source to query
            substitution: An optional initial substitution (pre-homomorphism)

        Yields:
            Substitutions that satisfy the query's formula
        """
        ...

    def evaluate_and_project(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: "Substitution" = None,
    ) -> Iterator[Tuple[Term, ...]]:
        """
        Evaluate a query and project results onto answer variables.

        This is a convenience method that evaluates the query and projects
        the resulting substitutions onto the answer variables, with deduplication.

        Args:
            query: The first-order query to evaluate
            data: The data source to query
            substitution: An optional initial substitution

        Yields:
            Deduplicated tuples of terms for answer variables
        """
        seen: set[Tuple[Term, ...]] = set()

        for result_sub in self.evaluate(query, data, substitution):
            answer = tuple(
                result_sub.apply(v) for v in query.answer_variables
            )
            if answer not in seen:
                seen.add(answer)
                yield answer
