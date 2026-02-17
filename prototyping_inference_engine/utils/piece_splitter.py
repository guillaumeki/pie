"""Piece-splitting abstractions and default implementation."""

from __future__ import annotations

from collections import deque
from typing import Iterable, Protocol, runtime_checkable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.variable import Variable


@runtime_checkable
class PieceSplitter(Protocol):
    """Split an atom set into variable-induced pieces."""

    def split(
        self, atom_set: AtomSet, active_variables: Iterable[Variable]
    ) -> tuple[FrozenAtomSet, ...]:
        """Return connected pieces induced by active variables."""


class VariableInducedPieceSplitter:
    """
    Default splitter: connected components induced by active variables.

    Ground atoms and atoms that do not contain active variables are ignored.
    """

    def split(
        self, atom_set: AtomSet, active_variables: Iterable[Variable]
    ) -> tuple[FrozenAtomSet, ...]:
        active = set(active_variables)
        if not active:
            return tuple()

        by_variable: dict[Variable, set[Atom]] = {var: set() for var in active}
        for atom in atom_set:
            atom_active_vars = atom.variables & active
            for var in atom_active_vars:
                by_variable[var].add(atom)

        visited_vars: set[Variable] = set()
        pieces: list[FrozenAtomSet] = []

        for root in active:
            if root in visited_vars or not by_variable[root]:
                continue

            queue: deque[Variable] = deque([root])
            visited_vars.add(root)
            component_atoms: set[Atom] = set()

            while queue:
                var = queue.popleft()
                for atom in by_variable[var]:
                    if atom in component_atoms:
                        continue
                    component_atoms.add(atom)
                    for linked_var in atom.variables & active:
                        if linked_var not in visited_vars:
                            visited_vars.add(linked_var)
                            queue.append(linked_var)

            if component_atoms:
                pieces.append(FrozenAtomSet(component_atoms))

        return tuple(pieces)
