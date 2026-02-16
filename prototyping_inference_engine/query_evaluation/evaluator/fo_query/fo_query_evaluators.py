"""
Concrete FOQueryEvaluator implementations for each formula type.
"""

# References:
# - "Foundations of Databases" —
#   Serge Abiteboul, Richard Hull, Victor Vianu.
#   Link: https://dl.acm.org/doi/book/10.5555/64510
#
# Summary:
# FO query evaluation decomposes formulas by logical connectives and quantifiers,
# reducing to conjunction evaluation and homomorphism checks for atoms.
#
# Properties used here:
# - Standard FO semantics for conjunction, disjunction, negation, and quantifiers.
#
# Implementation notes:
# This module provides the concrete evaluator classes that follow the FO
# semantics described in the reference.

from typing import Iterator, Type, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator import (
    FOQueryEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.prepared_queries import (
    PreparedBacktrackingConjunctiveFOQuery,
    PreparedDisjunctiveFOQuery,
    PreparedExistentialFOQuery,
    PreparedNegationFOQuery,
    PreparedUniversalFOQuery,
    prepare_atomic_or_conjunction,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.query.prepared_fo_query import PreparedFOQuery
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
        FOQueryEvaluatorRegistry,
    )


class AtomicFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with atomic formula."""

    @classmethod
    def supported_formula_type(cls) -> Type[Atom]:
        return Atom

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        prepared = self.prepare(query, data)
        initial = substitution if substitution is not None else Substitution()
        yield from prepared.execute(initial)

    def prepare(self, query: FOQuery, data: "ReadableData") -> "PreparedFOQuery":
        return prepare_atomic_or_conjunction(query, data)


class BacktrackingConjunctiveFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with conjunction formula using backtracking."""

    @classmethod
    def supported_formula_type(cls) -> Type[ConjunctionFormula]:
        return ConjunctionFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        prepared = self.prepare(query, data)
        initial = substitution if substitution is not None else Substitution()
        yield from prepared.execute(initial)

    def prepare(self, query: FOQuery, data: "ReadableData") -> "PreparedFOQuery":
        return PreparedBacktrackingConjunctiveFOQuery(query, data)


class DisjunctiveFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with disjunction formula."""

    @classmethod
    def supported_formula_type(cls) -> Type[DisjunctionFormula]:
        return DisjunctionFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        prepared = self.prepare(query, data)
        initial = substitution if substitution is not None else Substitution()
        yield from prepared.execute(initial)

    def prepare(self, query: FOQuery, data: "ReadableData") -> "PreparedFOQuery":
        return PreparedDisjunctiveFOQuery(query, data)


class NegationFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with negation formula."""

    @classmethod
    def supported_formula_type(cls) -> Type[NegationFormula]:
        return NegationFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        prepared = self.prepare(query, data)
        initial = substitution if substitution is not None else Substitution()
        yield from prepared.execute(initial)

    def prepare(self, query: FOQuery, data: "ReadableData") -> "PreparedFOQuery":
        return PreparedNegationFOQuery(query, data)


class UniversalFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with universal formula."""

    @classmethod
    def supported_formula_type(cls) -> Type[UniversalFormula]:
        return UniversalFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        prepared = self.prepare(query, data)
        initial = substitution if substitution is not None else Substitution()
        yield from prepared.execute(initial)

    def prepare(self, query: FOQuery, data: "ReadableData") -> "PreparedFOQuery":
        return PreparedUniversalFOQuery(query, data)


class ExistentialFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with existential formula."""

    @classmethod
    def supported_formula_type(cls) -> Type[ExistentialFormula]:
        return ExistentialFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        prepared = self.prepare(query, data)
        initial = substitution if substitution is not None else Substitution()
        yield from prepared.execute(initial)

    def prepare(self, query: FOQuery, data: "ReadableData") -> "PreparedFOQuery":
        return PreparedExistentialFOQuery(query, data)


class GenericFOQueryEvaluator(FOQueryEvaluator):
    """
    FOQueryEvaluator that delegates to the appropriate evaluator based on formula type.

    This is the main entry point for evaluating FOQuery instances when the
    formula type is not known in advance.
    """

    def __init__(self, registry: Optional["FOQueryEvaluatorRegistry"] = None):
        self._registry = registry

    def _get_registry(self) -> "FOQueryEvaluatorRegistry":
        if self._registry is None:
            from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
                FOQueryEvaluatorRegistry,
            )

            return FOQueryEvaluatorRegistry.instance()
        return self._registry

    @classmethod
    def supported_formula_type(cls):
        # This evaluator supports all formula types via delegation
        return None

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        from prototyping_inference_engine.query_evaluation.evaluator.errors import (
            UnsupportedFormulaError,
        )

        evaluator = self._get_registry().get_evaluator(query)
        if evaluator is None:
            raise UnsupportedFormulaError(type(query.formula))

        yield from evaluator.evaluate(query, data, substitution)

    def prepare(self, query: FOQuery, data: "ReadableData") -> "PreparedFOQuery":
        from prototyping_inference_engine.query_evaluation.evaluator.errors import (
            UnsupportedFormulaError,
        )

        evaluator = self._get_registry().get_evaluator(query)
        if evaluator is None:
            raise UnsupportedFormulaError(type(query.formula))

        return evaluator.prepare(query, data)
