"""
Atomic pattern for describing constraints on queryable predicates.
"""

from abc import ABC, abstractmethod
from typing import Optional, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.predicate import Predicate
    from prototyping_inference_engine.api.data.constraint.position_constraint import (
        PositionConstraint,
    )
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class AtomicPattern(ABC):
    """
    Describes constraints for querying a predicate from a data source.

    Some data sources require certain positions to have specific types of terms.
    For example, an API endpoint might require an ID (constant or literal) at
    position 0 to make a valid request.
    """

    @property
    @abstractmethod
    def predicate(self) -> "Predicate":
        """The predicate this pattern applies to."""
        ...

    @abstractmethod
    def get_constraint(self, position: int) -> Optional["PositionConstraint"]:
        """
        Get the constraint for a position, or None if unconstrained.

        Args:
            position: The position index (0-based)

        Returns:
            The constraint for this position, or None if any term is accepted
        """
        ...

    def can_evaluate_with(
        self, atom: "Atom", substitution: Optional["Substitution"] = None
    ) -> bool:
        """
        Check if an atom can be evaluated against this pattern.

        The atom's terms are first resolved using the substitution, then
        checked against the position constraints.

        Args:
            atom: The atom to check
            substitution: Optional substitution to apply before checking

        Returns:
            True if all constraints are satisfied
        """
        from prototyping_inference_engine.api.substitution.substitution import (
            Substitution,
        )

        if atom.predicate != self.predicate:
            return False

        sub = substitution or Substitution()

        for pos, term in enumerate(atom.terms):
            constraint = self.get_constraint(pos)
            if constraint is not None:
                resolved_term = sub.apply(term)
                if not constraint.is_satisfied_by(resolved_term):
                    return False
        return True

    def get_unsatisfied_positions(
        self, atom: "Atom", substitution: Optional["Substitution"] = None
    ) -> dict[int, "PositionConstraint"]:
        """
        Get positions whose constraints are not satisfied.

        Args:
            atom: The atom to check
            substitution: Optional substitution to apply before checking

        Returns:
            Dict mapping position index to the unsatisfied constraint
        """
        from prototyping_inference_engine.api.substitution.substitution import (
            Substitution,
        )

        sub = substitution or Substitution()
        unsatisfied = {}

        for pos, term in enumerate(atom.terms):
            constraint = self.get_constraint(pos)
            if constraint is not None:
                resolved_term = sub.apply(term)
                if not constraint.is_satisfied_by(resolved_term):
                    unsatisfied[pos] = constraint

        return unsatisfied


class UnconstrainedPattern(AtomicPattern):
    """Pattern with no constraints - any term at any position is accepted."""

    def __init__(self, predicate: "Predicate"):
        self._predicate = predicate

    @property
    def predicate(self) -> "Predicate":
        return self._predicate

    def get_constraint(self, position: int) -> Optional["PositionConstraint"]:
        return None

    def can_evaluate_with(
        self, atom: "Atom", substitution: Optional["Substitution"] = None
    ) -> bool:
        return atom.predicate == self._predicate

    def __repr__(self) -> str:
        return f"UnconstrainedPattern({self._predicate})"


class SimpleAtomicPattern(AtomicPattern):
    """Pattern with explicit constraints per position."""

    def __init__(
        self,
        predicate: "Predicate",
        constraints: Optional[Mapping[int, "PositionConstraint"]] = None,
    ):
        """
        Create a pattern with position constraints.

        Args:
            predicate: The predicate this pattern applies to
            constraints: Mapping from position index to constraint.
                        Positions not in the mapping are unconstrained.
        """
        self._predicate = predicate
        self._constraints: dict[int, "PositionConstraint"] = (
            dict(constraints) if constraints else {}
        )

    @property
    def predicate(self) -> "Predicate":
        return self._predicate

    @property
    def constrained_positions(self) -> frozenset[int]:
        """Positions that have constraints."""
        return frozenset(self._constraints.keys())

    def get_constraint(self, position: int) -> Optional["PositionConstraint"]:
        return self._constraints.get(position)

    def __repr__(self) -> str:
        if not self._constraints:
            return f"SimpleAtomicPattern({self._predicate})"
        constraints_str = ", ".join(
            f"{pos}: {c.description}" for pos, c in sorted(self._constraints.items())
        )
        return f"SimpleAtomicPattern({self._predicate}, {{{constraints_str}}})"
