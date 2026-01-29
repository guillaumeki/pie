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

    Example using from_formula:
        factory = FOQueryFactory(session)
        formula = session.formula().forall("X").atom("p", "X").build()
        query = factory.from_formula(formula, answer_variables=["X"])

    Example using builder:
        query = (factory.builder()
            .answer("X")
            .exists("Y")
            .atom("p", "X", "Y")
            .and_()
            .atom("q", "Y")
            .build())
        # Result: ?(X) :- ∃Y.(p(X,Y) ∧ q(Y))
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

        Args:
            formula: The formula defining the query
            answer_variables: Variable names or Variable objects for the answer
            label: Optional label for the query

        Returns:
            A new FOQuery instance with the same formula type
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

        Returns:
            A new FOQueryBuilder instance
        """
        return FOQueryBuilder(self._session)


class FOQueryBuilder:
    """
    Fluent builder for constructing first-order queries.

    The builder allows specifying answer variables and then building the formula
    using the same syntax as FormulaBuilder.

    Example:
        query = (FOQueryBuilder(session)
            .answer("X", "Y")
            .atom("p", "X", "Y")
            .and_()
            .atom("q", "Y")
            .not_()
            .build())
        # Result: ?(X, Y) :- (p(X,Y) ∧ ¬(q(Y)))

    Example with quantifiers:
        query = (FOQueryBuilder(session)
            .answer("X")
            .exists("Y")
            .atom("p", "X", "Y")
            .build())
        # Result: ?(X) :- ∃Y.p(X,Y)
    """

    def __init__(self, session: "ReasoningSession"):
        self._session = session
        self._answer_variables: list[Variable] = []
        self._formula_builder: Optional[FormulaBuilder] = None
        self._label: Optional[str] = None

    def _ensure_formula_builder(self) -> FormulaBuilder:
        """Lazily create the formula builder."""
        if self._formula_builder is None:
            self._formula_builder = self._session.formula()
        return self._formula_builder

    def label(self, label: str) -> "FOQueryBuilder":
        """
        Set an optional label for the query.

        Args:
            label: The label string

        Returns:
            self for chaining
        """
        self._label = label
        return self

    def answer(self, *var_names: str) -> "FOQueryBuilder":
        """
        Specify the answer variables for the query.

        Args:
            *var_names: Names of variables to include in the answer

        Returns:
            self for chaining
        """
        for name in var_names:
            self._answer_variables.append(self._session.variable(name))
        return self

    def atom(self, predicate_name: str, *term_names: str) -> "FOQueryBuilder":
        """
        Add an atomic formula.

        Term names starting with uppercase are treated as variables,
        otherwise as constants.

        Args:
            predicate_name: The predicate name
            *term_names: Names of terms

        Returns:
            self for chaining
        """
        self._ensure_formula_builder().atom(predicate_name, *term_names)
        return self

    def not_(self) -> "FOQueryBuilder":
        """
        Negate the last formula on the stack.

        Returns:
            self for chaining
        """
        self._ensure_formula_builder().not_()
        return self

    def and_(self) -> "FOQueryBuilder":
        """
        Mark that the next formula will be AND'd with the current one.

        Returns:
            self for chaining
        """
        self._ensure_formula_builder().and_()
        return self

    def or_(self) -> "FOQueryBuilder":
        """
        Mark that the next formula will be OR'd with the current one.

        Returns:
            self for chaining
        """
        self._ensure_formula_builder().or_()
        return self

    def forall(self, var_name: str) -> "FOQueryBuilder":
        """
        Add a universal quantifier.

        Args:
            var_name: The variable name to quantify

        Returns:
            self for chaining
        """
        self._ensure_formula_builder().forall(var_name)
        return self

    def exists(self, var_name: str) -> "FOQueryBuilder":
        """
        Add an existential quantifier.

        Args:
            var_name: The variable name to quantify

        Returns:
            self for chaining
        """
        self._ensure_formula_builder().exists(var_name)
        return self

    def build(self) -> FOQuery[Formula]:
        """
        Build the final FOQuery.

        Returns:
            The constructed FOQuery

        Raises:
            ValueError: If no formula has been built
        """
        if self._formula_builder is None:
            raise ValueError("No formula has been defined for the query")

        formula = self._formula_builder.build()
        return FOQuery(formula, self._answer_variables, self._label)
