from dataclasses import dataclass
from functools import cached_property

from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries
from prototyping_inference_engine.backward_chaining.unifier.piece_unifier import PieceUnifier


@dataclass(frozen=True)
class DisjunctivePieceUnifier:
    rule: Rule[ConjunctiveQuery, ConjunctiveQuery]
    piece_unifiers: tuple[PieceUnifier]
    query: UnionConjunctiveQueries

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
