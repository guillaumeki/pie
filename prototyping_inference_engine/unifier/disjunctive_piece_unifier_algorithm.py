#
# References:
# - "Query rewriting with disjunctive existential rules and mappings" —
#   Michel Leclere, Marie-Laure Mugnier, Guillaume Perution-Kihli.
#   Link: https://proceedings.kr.org/2023/42/
#
# Summary:
# The algorithm builds disjunctive piece-unifiers by combining piece-unifiers
# computed for each disjunctive head, preserving consistency across shared
# variables and partitions.
#
# Properties used here:
# - Soundness and completeness of disjunctive unifier enumeration.
# - Termination for rule sets where the underlying rewriting terminates.
#
# Implementation notes:
# This module implements the construction of partial disjunctive unifiers and
# their systematic extension, as described in the KR 2023 paper.

"""
Algorithm for computing disjunctive piece unifiers.
"""

from dataclasses import dataclass
from typing import Optional

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.ontology.rule.validators import ensure_ed_rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.unifier.disjunctive_piece_unifier import (
    DisjunctivePieceUnifier,
)
from prototyping_inference_engine.unifier.piece_unifier import (
    PieceUnifier,
)
from prototyping_inference_engine.unifier.piece_unifier_algorithm import (
    PieceUnifierAlgorithm,
)
from prototyping_inference_engine.unifier.piece_unifier_cache import (
    PieceUnifierCache,
)


@dataclass
class _PartialDisjunctivePieceUnifier:
    """Represents a partially constructed disjunctive piece unifier."""

    rule: Rule
    piece_unifiers: list[Optional[PieceUnifier]]
    cqs: list[Optional[ConjunctiveQuery]]
    answer_variables: tuple[Variable, ...]

    def to_disjunctive_piece_unifier(self):
        """Convert to a complete DisjunctivePieceUnifier."""
        return DisjunctivePieceUnifier(
            self.rule,
            tuple(self.piece_unifiers),
            UnionQuery[ConjunctiveQuery](self.cqs, self.answer_variables),
        )

    @property
    def partial_associated_partition(self):
        """Get the partition from all non-None piece unifiers."""
        it = iter(self.piece_unifiers)
        first = next(it)
        while not first:
            first = next(it)
        part = TermPartition(first.partition)

        for p in it:
            if p:
                part.join(p.partition)

        return part

    def partial_frontier_instantiation(
        self, head_number: int
    ) -> tuple[Optional[Term], ...]:
        """Get the frontier instantiation for a specific head."""
        instantiation: list[Optional[Term]] = []
        for v in self.rule.head_frontier(head_number):
            representative = self.partial_associated_partition.get_representative(v)
            if representative.is_ground:
                instantiation.append(representative)
            else:
                instantiation.append(None)
        return tuple(instantiation)


class DisjunctivePieceUnifierAlgorithm:
    """
    Algorithm for computing disjunctive piece unifiers.

    Uses a cache to store previously computed unifiers for incremental computation.
    """

    def __init__(self, cache: Optional[PieceUnifierCache] = None):
        self._cache = cache if cache is not None else PieceUnifierCache()

    def compute_disjunctive_unifiers(
        self,
        all_cqs: UnionQuery[ConjunctiveQuery],
        new_cqs: UnionQuery[ConjunctiveQuery],
        rule: Rule,
    ) -> set[DisjunctivePieceUnifier]:
        """
        Compute disjunctive piece unifiers for a rule and set of conjunctive queries.

        Args:
            all_cqs: All conjunctive queries seen so far
            new_cqs: New conjunctive queries to process
            rule: The rule to compute unifiers for

        Returns:
            Set of disjunctive piece unifiers
        """
        ensure_ed_rule(rule)
        self._cache.cleanup(set(all_cqs))
        self._cache.initialize_rule(rule)

        result: set[DisjunctivePieceUnifier] = set()

        for head_number, head in enumerate(rule.head_disjuncts):
            full_unifiers = self._compute_full_unifiers_of_a_ucq(
                rule, head_number, new_cqs
            )

            if full_unifiers and not self._cache.has_unifiers_for_head(
                rule, head_number
            ):
                self._cache.mark_has_unifiers(rule, head_number)

            if self._cache.has_unifiers_for_all_heads(rule):
                for fpu, cq in full_unifiers:
                    pdpu = self._create_partial_unifier(
                        rule, head_number, fpu, new_cqs.answer_variables
                    )
                    self._extend(rule, head_number, pdpu, result)

            # Store unifiers in cache
            for fpu, cq in full_unifiers:
                self._cache.store(cq, rule, head_number, fpu)

        return result

    def _create_partial_unifier(
        self,
        rule: Rule,
        head_number: int,
        unifier: PieceUnifier,
        answer_variables: tuple[Variable, ...],
    ) -> _PartialDisjunctivePieceUnifier:
        """Create a partial disjunctive piece unifier with one head filled in."""
        piece_unifiers: list[Optional[PieceUnifier]] = [None] * len(rule.head_disjuncts)
        cqs: list[Optional[ConjunctiveQuery]] = [None] * len(rule.head_disjuncts)
        piece_unifiers[head_number] = unifier
        cqs[head_number] = unifier.query
        return _PartialDisjunctivePieceUnifier(
            rule, piece_unifiers, cqs, answer_variables
        )

    def _extend(
        self,
        rule: Rule,
        head_number: int,
        pdpu: _PartialDisjunctivePieceUnifier,
        result: set[DisjunctivePieceUnifier],
        current_head: int = 0,
    ):
        """
        Recursively extend a partial unifier by filling in remaining heads.

        Args:
            rule: The rule being processed
            head_number: The head that was initially filled (skip this one)
            pdpu: The partial disjunctive piece unifier to extend
            result: Set to add complete unifiers to
            current_head: Current head index being processed
        """
        if current_head == len(rule.head_disjuncts):
            result.add(pdpu.to_disjunctive_piece_unifier())
        elif current_head != head_number:
            instantiation = pdpu.partial_frontier_instantiation(current_head)
            for unifier in self._cache.get_by_instantiation(
                rule, current_head, instantiation
            ):
                pdpu.piece_unifiers[current_head] = unifier
                pdpu.cqs[current_head] = unifier.query
                self._extend(rule, head_number, pdpu, result, current_head + 1)
        else:
            self._extend(rule, head_number, pdpu, result, current_head + 1)

    @staticmethod
    def _compute_full_unifiers_of_a_cq(
        rule: Rule,
        head_number: int,
        cq: ConjunctiveQuery,
    ) -> list[PieceUnifier]:
        """Compute full piece unifiers for a single conjunctive query."""
        return PieceUnifierAlgorithm.compute_most_general_full_piece_unifiers(
            Variable.safe_renaming_substitution(cq.existential_variables)(cq),
            Rule.extract_conjunctive_rule(rule, head_number),
        )

    @staticmethod
    def _compute_full_unifiers_of_a_ucq(
        rule: Rule,
        head_number: int,
        ucq: UnionQuery[ConjunctiveQuery],
    ) -> list[tuple[PieceUnifier, ConjunctiveQuery]]:
        """Compute full piece unifiers for all CQs in a UCQ."""
        return [
            (fpu, cq)
            for cq in ucq
            for fpu in DisjunctivePieceUnifierAlgorithm._compute_full_unifiers_of_a_cq(
                rule, head_number, cq
            )
        ]
