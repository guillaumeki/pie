"""
SessionCleanupStats dataclass for tracking cleanup operations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionCleanupStats:
    """
    Statistics from a session cleanup operation.

    Tracks how many terms and predicates were removed during cleanup.
    This class is immutable (frozen dataclass) and supports addition
    for accumulating stats across multiple cleanup operations.
    """

    variables_removed: int
    constants_removed: int
    predicates_removed: int

    @property
    def total_removed(self) -> int:
        """
        Return the total number of items removed.

        Returns:
            Sum of all removed items
        """
        return self.variables_removed + self.constants_removed + self.predicates_removed

    @property
    def is_empty(self) -> bool:
        """
        Return True if no items were removed.

        Returns:
            True if total_removed is 0
        """
        return self.total_removed == 0

    def __add__(self, other: "SessionCleanupStats") -> "SessionCleanupStats":
        """
        Add two cleanup stats together.

        Useful for accumulating stats across multiple cleanup operations.

        Args:
            other: Another SessionCleanupStats instance

        Returns:
            A new SessionCleanupStats with summed values
        """
        if not isinstance(other, SessionCleanupStats):
            return NotImplemented
        return SessionCleanupStats(
            variables_removed=self.variables_removed + other.variables_removed,
            constants_removed=self.constants_removed + other.constants_removed,
            predicates_removed=self.predicates_removed + other.predicates_removed,
        )

    def __repr__(self) -> str:
        """Return a human-readable representation."""
        return (
            f"SessionCleanupStats("
            f"variables={self.variables_removed}, "
            f"constants={self.constants_removed}, "
            f"predicates={self.predicates_removed}, "
            f"total={self.total_removed})"
        )
