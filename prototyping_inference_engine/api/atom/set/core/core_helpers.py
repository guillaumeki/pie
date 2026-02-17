"""Shared helpers for core algorithms."""

from __future__ import annotations

from typing import Iterable, Iterator

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution


def freeze_substitution(freeze: Iterable[Variable]) -> Substitution:
    """Build the identity pre-substitution for frozen variables."""
    return Substitution({v: v for v in freeze})


def identity_free(substitution: Substitution) -> Substitution:
    """Return substitution without identity mappings."""
    return Substitution({v: t for v, t in substitution.items() if v != t})


def atoms_with_variable(atom_set: AtomSet, variable: Variable) -> set[Atom]:
    """Return atoms from atom_set that contain variable."""
    return {atom for atom in atom_set if variable in atom.variables}


def atoms_with_variables(atom_set: AtomSet, variables: set[Variable]) -> set[Atom]:
    """Return atoms from atom_set containing at least one variable."""
    if not variables:
        return set()
    return {atom for atom in atom_set if atom.variables & variables}


def remove_atoms(mutable: MutableAtomSet, atoms: set[Atom]) -> None:
    """Remove atoms from mutable atom set."""
    for atom in atoms:
        mutable.discard(atom)


def remove_atoms_with_variables(
    mutable: MutableAtomSet, variables: set[Variable]
) -> set[Atom]:
    """Remove all atoms containing variables from mutable set."""
    to_remove = atoms_with_variables(mutable, variables)
    remove_atoms(mutable, to_remove)
    return to_remove


def without_atoms(atom_set: AtomSet, atoms_to_remove: set[Atom]) -> FrozenAtomSet:
    """Return immutable atom set without provided atoms."""
    return FrozenAtomSet(atom for atom in atom_set if atom not in atoms_to_remove)


def count_non_frozen_variables(atom_set: AtomSet, freeze: set[Variable]) -> int:
    """Count non-frozen variables used by atom_set."""
    return len({v for v in atom_set.variables if v not in freeze})


def substitution_external_range_variables(
    substitution: Substitution, in_piece_variables: set[Variable], frozen: set[Variable]
) -> set[Term]:
    """Range variables from substitution that are external to piece/freeze."""
    external: set[Term] = set()
    for term in substitution.image:
        if (
            isinstance(term, Variable)
            and term not in in_piece_variables
            and term not in frozen
        ):
            external.add(term)
    return external


def to_same_type(atom_set: AtomSet, atoms: Iterable[Atom]) -> AtomSet:
    """Rebuild an atom set using the same concrete type when possible."""
    cls = atom_set.__class__
    return cls(set(atoms))


def iter_homomorphisms(
    hom_algo,
    from_atom_set: AtomSet,
    to_atom_set: AtomSet,
    freeze_sub: Substitution,
) -> Iterator[Substitution]:
    """Compute homomorphisms with frozen-variable substitution."""
    return hom_algo.compute_homomorphisms(
        FrozenAtomSet(from_atom_set), FrozenAtomSet(to_atom_set), freeze_sub
    )
