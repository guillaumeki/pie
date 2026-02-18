"""Utilities combining multiple lineage trackers."""

from __future__ import annotations

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.forward_chaining.chase.lineage.lineage_tracker import (
    LineageTracker,
)


def get_ancestors_of(atom: Atom, *trackers: LineageTracker) -> set[Atom]:
    result: set[Atom] = set()
    todo = [atom]

    while todo:
        current = todo.pop(0)
        for tracker in trackers:
            for ancestor in tracker.get_prime_ancestors_of(current):
                if ancestor in result:
                    continue
                result.add(ancestor)
                todo.append(ancestor)

    return result
