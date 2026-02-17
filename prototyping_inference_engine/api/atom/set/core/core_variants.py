"""Core-processor variants and shared helper types."""

from enum import Enum


class CoreRetractionVariant(Enum):
    """Retraction strategy variants for by-piece processors."""

    EXHAUSTIVE = "exhaustive"
    BY_SPECIALISATION = "by_specialisation"
    BY_DELETION = "by_deletion"
