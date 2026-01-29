"""
Abstract base class for binary connective formulas.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from prototyping_inference_engine.api.formula.formula import Formula

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class BinaryFormula(Formula, ABC):
    """Base for binary connectives (AND, OR, etc.)."""

    def __init__(self, left: Formula, right: Formula):
        self._left = left
        self._right = right

    @property
    def left(self) -> Formula:
        """The left operand."""
        return self._left

    @property
    def right(self) -> Formula:
        """The right operand."""
        return self._right

    @property
    def free_variables(self) -> frozenset["Variable"]:
        return self._left.free_variables | self._right.free_variables

    @property
    def bound_variables(self) -> frozenset["Variable"]:
        return self._left.bound_variables | self._right.bound_variables

    @property
    def atoms(self) -> frozenset["Atom"]:
        return self._left.atoms | self._right.atoms

    @property
    @abstractmethod
    def symbol(self) -> str:
        """The symbol for this connective (∧, ∨, →, etc.)."""
        pass

    def __str__(self) -> str:
        return f"({self._left} {self.symbol} {self._right})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._left!r}, {self._right!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._left == other._left and self._right == other._right

    def __hash__(self) -> int:
        return hash((self.symbol, self._left, self._right))
