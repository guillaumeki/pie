"""Helpers to build hashable keys from substitutions."""

from __future__ import annotations

from prototyping_inference_engine.api.substitution.substitution import Substitution


def substitution_key(substitution: Substitution) -> tuple[tuple[object, object], ...]:
    normalized = substitution.normalize()
    return tuple(sorted(normalized.items(), key=lambda item: str(item[0])))
