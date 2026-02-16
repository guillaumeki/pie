#
# References:
# - "Query rewriting with disjunctive existential rules and mappings" —
#   Michel Leclere, Marie-Laure Mugnier, Guillaume Perution-Kihli.
#   Link: https://doi.org/10.24963/kr.2023/59
#
# Summary:
# Disjunctive piece-unifiers extend piece-unifiers to rules with disjunctive
# heads by combining unifiers for each disjunct and tracking a global partition.
#
# Properties used here:
# - Soundness and completeness of disjunctive unification for disjunctive heads.
# - Compatibility constraints ensure correct handling of shared frontier terms.
#
# Implementation notes:
# This class stores a tuple of piece-unifiers (one per disjunct) and builds the
# associated partition/substitution used during disjunctive rewriting.

from dataclasses import dataclass
from functools import cached_property

from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.unifier.piece_unifier import (
    PieceUnifier,
)


@dataclass(frozen=True)
class DisjunctivePieceUnifier:
    rule: Rule
    piece_unifiers: tuple[PieceUnifier]
    query: UnionQuery[ConjunctiveQuery]

    @cached_property
    def associated_partition(self):
        it = iter(self.piece_unifiers)
        part = TermPartition(next(it).partition)

        for p in it:
            part.join(p.partition)
            for v, t in p.query.pre_substitution.graph:
                part.union(v, t)

        return part

    @cached_property
    def associated_substitution(self):
        return self.associated_partition.associated_substitution(self.query)
