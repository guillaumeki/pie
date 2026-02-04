"""
Abstract base class for quantified formulas.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.formula.formula import Formula

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class QuantifiedFormula(Formula, ABC):
    """Base for quantified formulas (∀, ∃)."""

    def __init__(self, variable: "Variable", formula: Formula):
        self._variable = variable
        self._formula = formula

    @property
    def variable(self) -> "Variable":
        """The quantified variable."""
        return self._variable

    @property
    def inner(self) -> Formula:
        """The formula under the quantifier."""
        return self._formula

    @property
    def free_variables(self) -> frozenset["Variable"]:
        # The quantified variable is bound, so not free
        return self._formula.free_variables - {self._variable}

    @property
    def bound_variables(self) -> frozenset["Variable"]:
        return self._formula.bound_variables | {self._variable}

    @property
    def atoms(self) -> frozenset["Atom"]:
        return self._formula.atoms

    @property
    @abstractmethod
    def quantifier_symbol(self) -> str:
        """The symbol for this quantifier (∀, ∃)."""
        pass

    def apply_substitution(self, substitution: "Substitution") -> "QuantifiedFormula":
        from prototyping_inference_engine.api.atom.term.variable import Variable
        from prototyping_inference_engine.api.substitution.substitution import (
            Substitution,
        )

        # Don't substitute the bound variable
        restricted_sub = Substitution(
            {k: v for k, v in substitution.items() if k != self._variable}
        )

        # Avoid variable capture: if the bound variable appears in the range of the
        # substitution, rename it to a fresh variable
        sub_range_vars = {v for v in restricted_sub.values() if isinstance(v, Variable)}
        if self._variable in sub_range_vars:
            fresh = Variable.fresh_variable()
            inner_renamed = self._formula.apply_substitution(
                Substitution({self._variable: fresh})
            )
            return self.__class__(
                fresh, inner_renamed.apply_substitution(restricted_sub)
            )

        return self.__class__(
            self._variable, self._formula.apply_substitution(restricted_sub)
        )

    def __str__(self) -> str:
        return f"{self.quantifier_symbol}{self._variable}.({self._formula})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._variable!r}, {self._formula!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._variable == other._variable and self._formula == other._formula

    def __hash__(self) -> int:
        return hash((self.quantifier_symbol, self._variable, self._formula))
