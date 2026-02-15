"""
Dependency checkers for GRD.
"""

from abc import ABC, abstractmethod
from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.grd.rule_utils import (
    extract_head_conjunction,
    extract_head_disjunct_conjunctions,
    extract_negative_body,
    extract_positive_body,
)
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.unifier.piece_unifier import PieceUnifier


class DependencyChecker(ABC):
    @abstractmethod
    def is_valid_positive_dependency(
        self, r1: Rule, r2: Rule, unifier: PieceUnifier
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_valid_negative_dependency(
        self, r1: Rule, r2: Rule, unifier: PieceUnifier
    ) -> bool:
        raise NotImplementedError


class ProductivityChecker(DependencyChecker):
    def is_valid_positive_dependency(
        self, r1: Rule, r2: Rule, unifier: PieceUnifier
    ) -> bool:
        substitution = unifier.associated_substitution
        if substitution is None:
            return False

        bpr1 = _apply_to_atoms(extract_positive_body(r1).atoms, substitution)
        bnr1 = _apply_to_atoms(extract_negative_body(r1).atoms, substitution)
        hr1 = _apply_to_atoms(extract_head_conjunction(r1.head).atoms, substitution)

        bpr2 = _apply_to_atoms(extract_positive_body(r2).atoms, substitution)
        bnr2 = _apply_to_atoms(extract_negative_body(r2).atoms, substitution)
        hr2_disjuncts = [
            _apply_to_atoms(cq.atoms, substitution)
            for cq in extract_head_disjunct_conjunctions(r2)
        ]

        return (
            not bpr1.intersection(bnr1)
            and not bpr1.intersection(bnr2)
            and not bpr2.intersection(bnr2)
            and not bpr2.intersection(bnr1 - hr1)
            and not _all_disjuncts_contained(bpr1 | hr1 | bpr2, hr2_disjuncts)
            and not bnr2.intersection(hr1)
            and not _contains_all(bpr1, bpr2)
        )

    def is_valid_negative_dependency(
        self, r1: Rule, r2: Rule, unifier: PieceUnifier
    ) -> bool:
        substitution = unifier.associated_substitution
        if substitution is None:
            return False

        bpr1 = _apply_to_atoms(extract_positive_body(r1).atoms, substitution)
        bnr1 = _apply_to_atoms(extract_negative_body(r1).atoms, substitution)
        bpr2 = _apply_to_atoms(extract_positive_body(r2).atoms, substitution)
        bnr2 = _apply_to_atoms(extract_negative_body(r2).atoms, substitution)

        return not (bpr1 | bpr2).intersection(bnr1 | bnr2)


def _apply_to_atoms(atoms: Iterable[Atom], substitution: Substitution) -> set[Atom]:
    return set(substitution(list(atoms)))


def _contains_all(source: set[Atom], target: set[Atom]) -> bool:
    return target.issubset(source)


def _all_disjuncts_contained(source: set[Atom], disjuncts: list[set[Atom]]) -> bool:
    if not disjuncts:
        return False
    return all(_contains_all(source, disjunct) for disjunct in disjuncts)
