"""
Cache for piece unifiers used in disjunctive piece unifier computation.

This class manages the storage and retrieval of piece unifiers to optimize
incremental computation of disjunctive unifiers.
"""

from collections import defaultdict
from typing import Optional, Iterable

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.unifier.piece_unifier import (
    PieceUnifier,
)


class PieceUnifierCache:
    """
    Cache for storing and retrieving piece unifiers.

    The cache is organized by:
    - Conjunctive query (CQ) that was unified
    - Rule used for unification
    - Head number in the rule
    - Frontier instantiation (tuple of constants/None)
    """

    def __init__(self):
        # Cache structure: CQ -> Rule -> head_number -> instantiation -> list[PieceUnifier]
        self._unifiers: defaultdict[
            ConjunctiveQuery,
            defaultdict[
                Rule,
                defaultdict[
                    int, defaultdict[tuple[Optional[Term], ...], list[PieceUnifier]]
                ],
            ],
        ] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        )

        # Track which rules have unifiers for each head
        self._has_unifiers: dict[Rule, list[bool]] = {}

    def store(
        self, cq: ConjunctiveQuery, rule: Rule, head_number: int, unifier: PieceUnifier
    ) -> None:
        """Store a piece unifier in the cache."""
        self._unifiers[cq][rule][head_number][unifier.frontier_instantiation].append(
            unifier
        )

    def get_by_instantiation(
        self, rule: Rule, head_number: int, instantiation: tuple[Optional[Term], ...]
    ) -> Iterable[PieceUnifier]:
        """Get all unifiers matching the given instantiation."""
        for cq in self._unifiers:
            for inst, unifiers in self._unifiers[cq][rule][head_number].items():
                if self._is_instantiation_compatible(instantiation, inst):
                    yield from unifiers

    def get_compatible_unifiers(
        self,
        rule: Rule,
        head_number: int,
        reference_instantiation: tuple[Optional[Term], ...],
    ) -> Iterable[PieceUnifier]:
        """Get all unifiers with instantiation more specific than reference."""
        for cq in self._unifiers:
            for inst, unifiers in self._unifiers[cq][rule][head_number].items():
                if self._is_instantiation_more_general_than(
                    reference_instantiation, inst
                ):
                    yield from unifiers

    def cleanup(self, valid_cqs: set[ConjunctiveQuery]) -> None:
        """Remove cached entries for CQs that are no longer valid."""
        stale_cqs = set(self._unifiers.keys()) - valid_cqs
        for cq in stale_cqs:
            del self._unifiers[cq]

    def mark_has_unifiers(self, rule: Rule, head_number: int) -> None:
        """Mark that unifiers exist for a specific rule head."""
        if rule not in self._has_unifiers:
            self._has_unifiers[rule] = [False] * len(rule.head_disjuncts)
        self._has_unifiers[rule][head_number] = True

    def has_unifiers_for_head(self, rule: Rule, head_number: int) -> bool:
        """Check if unifiers exist for a specific rule head."""
        if rule not in self._has_unifiers:
            return False
        return self._has_unifiers[rule][head_number]

    def has_unifiers_for_all_heads(self, rule: Rule) -> bool:
        """Check if unifiers exist for all heads of a rule."""
        if rule not in self._has_unifiers:
            return False
        return all(self._has_unifiers[rule])

    def initialize_rule(self, rule: Rule) -> None:
        """Initialize tracking for a rule if not already done."""
        if rule not in self._has_unifiers:
            self._has_unifiers[rule] = [False] * len(rule.head_disjuncts)

    @staticmethod
    def _is_instantiation_more_general_than(
        i1: tuple[Optional[Term], ...], i2: tuple[Optional[Term], ...]
    ) -> bool:
        """Check if i1 is more general than i2 (i1 has None where i2 has values)."""
        return all(c1 is None or c1 == c2 for c1, c2 in zip(i1, i2))

    @staticmethod
    def _is_instantiation_compatible(
        i1: tuple[Optional[Term], ...], i2: tuple[Optional[Term], ...]
    ) -> bool:
        """Check if two instantiations are compatible (no conflicts)."""
        return all(c1 is None or c2 is None or c1 == c2 for c1, c2 in zip(i1, i2))
