"""Formula helpers for forward chaining."""

from __future__ import annotations

from collections import deque
from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.formula.binary_formula import BinaryFormula
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula


def conjunction_from_atoms(atoms: Iterable[Atom]) -> Formula | None:
    atoms_list = list(atoms)
    if not atoms_list:
        return None
    result: Formula = atoms_list[0]
    for atom in atoms_list[1:]:
        result = ConjunctionFormula(result, atom)
    return result


def split_conjunction_atoms(formula: Formula) -> list[Atom]:
    if isinstance(formula, Atom):
        return [formula]
    if isinstance(formula, ConjunctionFormula):
        return split_conjunction_atoms(formula.left) + split_conjunction_atoms(
            formula.right
        )
    if isinstance(formula, (ExistentialFormula, UniversalFormula)):
        return split_conjunction_atoms(formula.inner)
    if isinstance(formula, NegationFormula):
        return []
    if isinstance(formula, DisjunctionFormula):
        raise ValueError("Disjunction is not supported in this conjunction fragment")
    if isinstance(formula, BinaryFormula):
        return split_conjunction_atoms(formula.left) + split_conjunction_atoms(
            formula.right
        )
    raise ValueError(f"Unsupported formula type: {type(formula)}")


def split_disjunction_formulas(formula: Formula) -> list[Formula]:
    if isinstance(formula, DisjunctionFormula):
        return split_disjunction_formulas(formula.left) + split_disjunction_formulas(
            formula.right
        )
    return [formula]


def split_into_single_piece_heads(formula: Formula) -> list[Formula]:
    """Split a conjunction head into variable-induced pieces."""
    atoms = split_conjunction_atoms(formula)
    if len(atoms) <= 1:
        return [formula]

    adjacency: dict[int, set[int]] = {idx: set() for idx in range(len(atoms))}

    var_to_atoms: dict[object, set[int]] = {}
    for idx, atom in enumerate(atoms):
        for var in atom.variables:
            var_to_atoms.setdefault(var, set()).add(idx)

    for indexes in var_to_atoms.values():
        idxs = list(indexes)
        for i in idxs:
            adjacency[i].update(indexes - {i})

    visited: set[int] = set()
    pieces: list[list[Atom]] = []

    for root in range(len(atoms)):
        if root in visited:
            continue
        queue = deque([root])
        visited.add(root)
        piece: list[Atom] = []
        while queue:
            idx = queue.popleft()
            piece.append(atoms[idx])
            for nxt in adjacency[idx]:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        pieces.append(piece)

    formulas: list[Formula] = []
    for piece in pieces:
        piece_formula = conjunction_from_atoms(piece)
        if piece_formula is not None:
            formulas.append(piece_formula)
    return formulas if formulas else [formula]
