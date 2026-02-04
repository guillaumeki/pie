"""
Position constraint base class and common constraints.
"""

from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.term import Term


class PositionConstraint(ABC):
    """Constraint on the term expected at a position."""

    @abstractmethod
    def is_satisfied_by(self, term: "Term") -> bool:
        """Check if the term satisfies this constraint."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description for error messages."""
        ...

    def __and__(self, other: "PositionConstraint") -> "PositionConstraint":
        """Combine constraints with AND."""
        return AllOfConstraint(self, other)

    def __or__(self, other: "PositionConstraint") -> "PositionConstraint":
        """Combine constraints with OR."""
        return AnyOfConstraint(self, other)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.description})"


class GroundConstraint(PositionConstraint):
    """Term must be ground (not a variable)."""

    def is_satisfied_by(self, term: "Term") -> bool:
        from prototyping_inference_engine.api.atom.term.variable import Variable

        return not isinstance(term, Variable)

    @property
    def description(self) -> str:
        return "ground"


class ConstantConstraint(PositionConstraint):
    """Term must be a Constant."""

    def is_satisfied_by(self, term: "Term") -> bool:
        from prototyping_inference_engine.api.atom.term.constant import Constant

        return isinstance(term, Constant)

    @property
    def description(self) -> str:
        return "constant"


class VariableConstraint(PositionConstraint):
    """Term must be a Variable."""

    def is_satisfied_by(self, term: "Term") -> bool:
        from prototyping_inference_engine.api.atom.term.variable import Variable

        return isinstance(term, Variable)

    @property
    def description(self) -> str:
        return "variable"


class PredicateConstraint(PositionConstraint):
    """Custom constraint using a predicate function."""

    def __init__(
        self, predicate: Callable[["Term"], bool], description: str = "custom"
    ):
        self._predicate = predicate
        self._description = description

    def is_satisfied_by(self, term: "Term") -> bool:
        return self._predicate(term)

    @property
    def description(self) -> str:
        return self._description


class AnyOfConstraint(PositionConstraint):
    """At least one constraint must be satisfied (OR)."""

    def __init__(self, *constraints: PositionConstraint):
        if not constraints:
            raise ValueError("AnyOfConstraint requires at least one constraint")
        self._constraints = constraints

    @property
    def constraints(self) -> tuple[PositionConstraint, ...]:
        """The constraints being combined."""
        return self._constraints

    def is_satisfied_by(self, term: "Term") -> bool:
        return any(c.is_satisfied_by(term) for c in self._constraints)

    @property
    def description(self) -> str:
        return "(" + " | ".join(c.description for c in self._constraints) + ")"


class AllOfConstraint(PositionConstraint):
    """All constraints must be satisfied (AND)."""

    def __init__(self, *constraints: PositionConstraint):
        if not constraints:
            raise ValueError("AllOfConstraint requires at least one constraint")
        self._constraints = constraints

    @property
    def constraints(self) -> tuple[PositionConstraint, ...]:
        """The constraints being combined."""
        return self._constraints

    def is_satisfied_by(self, term: "Term") -> bool:
        return all(c.is_satisfied_by(term) for c in self._constraints)

    @property
    def description(self) -> str:
        return "(" + " & ".join(c.description for c in self._constraints) + ")"


# Singleton instances for common constraints
GROUND = GroundConstraint()
CONSTANT = ConstantConstraint()
VARIABLE = VariableConstraint()
