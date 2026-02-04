"""
Concrete FOQueryEvaluator implementations for each formula type.
"""

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
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator import (
    FOQueryEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.atom.atom_evaluator import (
    AtomEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.conjunction.backtrack_conjunction_evaluator import (
    BacktrackConjunctionEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.disjunction.disjunction_formula_evaluator import (
    DisjunctionFormulaEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.negation.negation_formula_evaluator import (
    NegationFormulaEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.quantifiers.universal_formula_evaluator import (
    UniversalFormulaEvaluator,
)
from prototyping_inference_engine.query_evaluation.evaluator.quantifiers.existential_formula_evaluator import (
    ExistentialFormulaEvaluator,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.api.substitution.substitution import Substitution
    from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
        FOQueryEvaluatorRegistry,
    )


class AtomicFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with atomic formula."""

    def __init__(self):
        self._formula_evaluator = AtomEvaluator()

    @classmethod
    def supported_formula_type(cls) -> Type[Atom]:
        return Atom

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        yield from self._formula_evaluator.evaluate(query.formula, data, substitution)


class ConjunctiveFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with conjunction formula."""

    def __init__(self, registry: Optional["FOQueryEvaluatorRegistry"] = None):
        self._registry = registry
        self._formula_evaluator: Optional[BacktrackConjunctionEvaluator] = None

    def _get_formula_evaluator(self) -> BacktrackConjunctionEvaluator:
        if self._formula_evaluator is None:
            self._formula_evaluator = BacktrackConjunctionEvaluator()
        return self._formula_evaluator

    @classmethod
    def supported_formula_type(cls) -> Type[ConjunctionFormula]:
        return ConjunctionFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        yield from self._get_formula_evaluator().evaluate(
            query.formula, data, substitution
        )


class DisjunctiveFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with disjunction formula."""

    def __init__(self, registry: Optional["FOQueryEvaluatorRegistry"] = None):
        self._registry = registry
        self._formula_evaluator: Optional[DisjunctionFormulaEvaluator] = None

    def _get_formula_evaluator(self) -> DisjunctionFormulaEvaluator:
        if self._formula_evaluator is None:
            self._formula_evaluator = DisjunctionFormulaEvaluator()
        return self._formula_evaluator

    @classmethod
    def supported_formula_type(cls) -> Type[DisjunctionFormula]:
        return DisjunctionFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        yield from self._get_formula_evaluator().evaluate(
            query.formula, data, substitution
        )


class NegationFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with negation formula."""

    def __init__(self, registry: Optional["FOQueryEvaluatorRegistry"] = None):
        self._registry = registry
        self._formula_evaluator: Optional[NegationFormulaEvaluator] = None

    def _get_formula_evaluator(self) -> NegationFormulaEvaluator:
        if self._formula_evaluator is None:
            self._formula_evaluator = NegationFormulaEvaluator()
        return self._formula_evaluator

    @classmethod
    def supported_formula_type(cls) -> Type[NegationFormula]:
        return NegationFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        yield from self._get_formula_evaluator().evaluate(
            query.formula, data, substitution
        )


class UniversalFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with universal formula."""

    def __init__(self, registry: Optional["FOQueryEvaluatorRegistry"] = None):
        self._registry = registry
        self._formula_evaluator: Optional[UniversalFormulaEvaluator] = None

    def _get_formula_evaluator(self) -> UniversalFormulaEvaluator:
        if self._formula_evaluator is None:
            self._formula_evaluator = UniversalFormulaEvaluator()
        return self._formula_evaluator

    @classmethod
    def supported_formula_type(cls) -> Type[UniversalFormula]:
        return UniversalFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        yield from self._get_formula_evaluator().evaluate(
            query.formula, data, substitution
        )


class ExistentialFOQueryEvaluator(FOQueryEvaluator):
    """Evaluator for FOQuery with existential formula."""

    def __init__(self, registry: Optional["FOQueryEvaluatorRegistry"] = None):
        self._registry = registry
        self._formula_evaluator: Optional[ExistentialFormulaEvaluator] = None

    def _get_formula_evaluator(self) -> ExistentialFormulaEvaluator:
        if self._formula_evaluator is None:
            self._formula_evaluator = ExistentialFormulaEvaluator()
        return self._formula_evaluator

    @classmethod
    def supported_formula_type(cls) -> Type[ExistentialFormula]:
        return ExistentialFormula

    def evaluate(
        self,
        query: FOQuery,
        data: "ReadableData",
        substitution: Optional["Substitution"] = None,
    ) -> Iterator["Substitution"]:
        yield from self._get_formula_evaluator().evaluate(
            query.formula, data, substitution
        )


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
