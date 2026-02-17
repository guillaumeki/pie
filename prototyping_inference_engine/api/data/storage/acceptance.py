"""Acceptance contracts for constrained writable storages."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AcceptanceResult:
    """Result of checking if an atom/predicate is accepted by a storage."""

    accepted: bool
    reason: str | None = None

    @staticmethod
    def ok() -> "AcceptanceResult":
        return AcceptanceResult(True, None)

    @staticmethod
    def reject(reason: str) -> "AcceptanceResult":
        return AcceptanceResult(False, reason)
