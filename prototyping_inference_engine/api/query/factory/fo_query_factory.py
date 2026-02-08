"""
Factory for creating first-order queries.
"""

from typing import Optional, TYPE_CHECKING, TypeVar, Union

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.formula_builder import FormulaBuilder
from prototyping_inference_engine.api.query.fo_query import FOQuery

if TYPE_CHECKING:
    from prototyping_inference_engine.session.reasoning_session import ReasoningSession

F = TypeVar("F", bound=Formula)


class FOQueryFactory:
    """
    Factory for creating first-order queries.

    Provides multiple ways to create FOQuery instances:
    1. From an existing Formula
    2. Using a fluent builder API
    """

    def __init__(self, session: "ReasoningSession"):
        self._session = session

    def from_formula(
        self,
        formula: F,
        answer_variables: Optional[list[Union[str, Variable]]] = None,
        label: Optional[str] = None,
    ) -> FOQuery[F]:
        """
        Create a FOQuery from an existing formula.
        """
        vars_list: list[Variable] = []
        if answer_variables:
            for v in answer_variables:
                if isinstance(v, str):
                    vars_list.append(self._session.variable(v))
                else:
                    vars_list.append(v)
        return FOQuery(formula, vars_list, label)

    def builder(self) -> "FOQueryBuilder":
        """
        Create a fluent builder for constructing a FOQuery.
        """
        return FOQueryBuilder(self._session)


class FOQueryBuilder:
    """
    Fluent builder for constructing first-order queries.
    """

    def __init__(self, session: "ReasoningSession"):
        self._session = session
        self._answer_variables: list[Variable] = []
        self._formula_builder: Optional[FormulaBuilder] = None
        self._label: Optional[str] = None

    def _ensure_formula_builder(self) -> FormulaBuilder:
        if self._formula_builder is None:
            self._formula_builder = self._session.formula()
        return self._formula_builder

    def label(self, label: str) -> "FOQueryBuilder":
        self._label = label
        return self

    def answer(self, *var_names: str) -> "FOQueryBuilder":
        for name in var_names:
            self._answer_variables.append(self._session.variable(name))
        return self

    def atom(self, predicate_name: str, *term_names: str) -> "FOQueryBuilder":
        self._ensure_formula_builder().atom(predicate_name, *term_names)
        return self

    def not_(self) -> "FOQueryBuilder":
        self._ensure_formula_builder().not_()
        return self

    def and_(self) -> "FOQueryBuilder":
        self._ensure_formula_builder().and_()
        return self

    def or_(self) -> "FOQueryBuilder":
        self._ensure_formula_builder().or_()
        return self

    def forall(self, var_name: str) -> "FOQueryBuilder":
        self._ensure_formula_builder().forall(var_name)
        return self

    def exists(self, var_name: str) -> "FOQueryBuilder":
        self._ensure_formula_builder().exists(var_name)
        return self

    def build(self) -> FOQuery:
        builder = self._ensure_formula_builder()
        formula = builder.build()
        return FOQuery(formula, self._answer_variables, self._label)
