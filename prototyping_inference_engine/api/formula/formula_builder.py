"""
Fluent builder for constructing first-order formulas.
"""
from typing import TYPE_CHECKING, Union

from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.api.formula.disjunction_formula import DisjunctionFormula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.formula.existential_formula import ExistentialFormula

if TYPE_CHECKING:
    from prototyping_inference_engine.session.reasoning_session import ReasoningSession
    from prototyping_inference_engine.api.atom.term.variable import Variable


class _OperatorMarker:
    """Base class for operator markers in the stack."""
    pass


class _AndMarker(_OperatorMarker):
    """Marker for pending AND operation."""
    pass


class _OrMarker(_OperatorMarker):
    """Marker for pending OR operation."""
    pass


class FormulaBuilder:
    """
    Fluent builder for constructing first-order formulas.

    Example:
        builder = FormulaBuilder(session)
        formula = (builder
            .forall("X")
            .exists("Y")
            .atom("p", "X", "Y")
            .and_()
            .atom("q", "Y")
            .build())
        # Result: ∀X.∃Y.(p(X,Y) ∧ q(Y))
    """

    def __init__(self, session: "ReasoningSession"):
        self._session = session
        self._stack: list[Union[Formula, _OperatorMarker]] = []
        self._quantifiers: list[tuple[str, "Variable"]] = []  # ('forall'|'exists', var)

    def atom(self, predicate_name: str, *term_names: str) -> "FormulaBuilder":
        """
        Add an atomic formula.

        Term names starting with uppercase are treated as variables,
        otherwise as constants.

        Args:
            predicate_name: The predicate name
            *term_names: Names of terms (variables if uppercase, constants otherwise)

        Returns:
            self for chaining
        """
        from prototyping_inference_engine.api.atom.term.term import Term

        terms: list[Term] = []
        for name in term_names:
            if name[0].isupper():
                terms.append(self._session.variable(name))
            else:
                terms.append(self._session.constant(name))
        pred = self._session.predicate(predicate_name, len(terms))
        atom = self._session.atom(pred, *terms)
        self._stack.append(atom)
        return self

    def not_(self) -> "FormulaBuilder":
        """
        Negate the last formula on the stack.

        Returns:
            self for chaining

        Raises:
            ValueError: If the stack is empty
        """
        if not self._stack:
            raise ValueError("No formula to negate")
        item = self._stack.pop()
        if isinstance(item, _OperatorMarker):
            raise ValueError("Cannot negate an operator marker")
        self._stack.append(NegationFormula(item))
        return self

    def and_(self) -> "FormulaBuilder":
        """
        Mark that the next formula will be AND'd with the current one.

        Returns:
            self for chaining
        """
        self._stack.append(_AndMarker())
        return self

    def or_(self) -> "FormulaBuilder":
        """
        Mark that the next formula will be OR'd with the current one.

        Returns:
            self for chaining
        """
        self._stack.append(_OrMarker())
        return self

    def forall(self, var_name: str) -> "FormulaBuilder":
        """
        Add a universal quantifier.

        Args:
            var_name: The variable name to quantify

        Returns:
            self for chaining
        """
        var = self._session.variable(var_name)
        self._quantifiers.append(('forall', var))
        return self

    def exists(self, var_name: str) -> "FormulaBuilder":
        """
        Add an existential quantifier.

        Args:
            var_name: The variable name to quantify

        Returns:
            self for chaining
        """
        var = self._session.variable(var_name)
        self._quantifiers.append(('exists', var))
        return self

    def build(self) -> Formula:
        """
        Build the final formula.

        Returns:
            The constructed Formula

        Raises:
            ValueError: If the stack cannot be reduced to a single formula
        """
        # Reduce stack to single formula
        formula = self._reduce_stack()

        # Apply quantifiers (in reverse order)
        for quant_type, var in reversed(self._quantifiers):
            if quant_type == 'forall':
                formula = UniversalFormula(var, formula)
            else:
                formula = ExistentialFormula(var, formula)

        return formula

    def _reduce_stack(self) -> Formula:
        """Reduce the stack by applying operators."""
        result: list[Union[Formula, _OperatorMarker]] = []

        for item in self._stack:
            if isinstance(item, _AndMarker):
                if len(result) < 1 or isinstance(result[-1], _OperatorMarker):
                    raise ValueError("AND requires a left operand")
                result.append(item)
            elif isinstance(item, _OrMarker):
                if len(result) < 1 or isinstance(result[-1], _OperatorMarker):
                    raise ValueError("OR requires a left operand")
                result.append(item)
            elif isinstance(item, Formula):
                if result and isinstance(result[-1], _AndMarker):
                    result.pop()  # Remove marker
                    left = result.pop()
                    if not isinstance(left, Formula):
                        raise ValueError("Invalid formula stack state")
                    result.append(ConjunctionFormula(left, item))
                elif result and isinstance(result[-1], _OrMarker):
                    result.pop()  # Remove marker
                    left = result.pop()
                    if not isinstance(left, Formula):
                        raise ValueError("Invalid formula stack state")
                    result.append(DisjunctionFormula(left, item))
                else:
                    result.append(item)

        if len(result) != 1:
            raise ValueError(f"Invalid formula: stack has {len(result)} items after reduction")

        final = result[0]
        if not isinstance(final, Formula):
            raise ValueError("Final result is not a formula")

        return final
