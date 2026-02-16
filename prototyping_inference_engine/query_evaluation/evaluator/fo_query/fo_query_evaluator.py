"""
Abstract base class for first-order query evaluators.
"""

# References:
# - "Foundations of Databases" —
#   Serge Abiteboul, Richard Hull, Victor Vianu.
#   Link: https://dl.acm.org/doi/book/10.5555/64510
#
# Summary:
# FO queries are evaluated by interpreting their formulas over a database
# instance, with conjunctive queries handled via homomorphisms.
#
# Properties used here:
# - Standard FO semantics and CQ homomorphism characterization.
#
# Implementation notes:
# This base class defines the evaluator interface used to dispatch on formula
# types in the query evaluation stack.

from abc import abstractmethod
from typing import Iterator, Tuple, Type, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.query_evaluation.evaluator.query.query_evaluator import (
    QueryEvaluator,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.query.prepared_fo_query import PreparedFOQuery
    from prototyping_inference_engine.api.substitution.substitution import Substitution


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
        substitution: Optional["Substitution"] = None,
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

    @abstractmethod
    def prepare(self, query: FOQuery, data: "ReadableData") -> "PreparedFOQuery":
        """Prepare a query against a data source for repeated evaluation."""
        ...

    def evaluate_and_project(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
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
            answer = tuple(result_sub.apply(v) for v in query.answer_variables)
            if answer not in seen:
                seen.add(answer)
                yield answer
