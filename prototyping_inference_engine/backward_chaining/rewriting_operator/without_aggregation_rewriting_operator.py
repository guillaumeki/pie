#
# References:
# - "Query rewriting with disjunctive existential rules and mappings" —
#   Michel Leclere, Marie-Laure Mugnier, Guillaume Perution-Kihli.
#   Link: https://proceedings.kr.org/2023/42/
#
# Summary:
# This rewriting operator applies disjunctive piece-unifiers to transform UCQs
# when rules have disjunctive heads, producing a UCQ that preserves answers.
#
# Properties used here:
# - Soundness and completeness of disjunctive rewriting.
# - Termination guarantees under the same conditions as the underlying algorithm.
#
# Implementation notes:
# This operator implements the disjunctive rewriting step from the KR 2023 paper
# by constructing new CQs from disjunctive piece-unifiers.

from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.backward_chaining.rewriting_operator.rewriting_operator import (
    RewritingOperator,
)
from prototyping_inference_engine.unifier.disjunctive_piece_unifier import (
    DisjunctivePieceUnifier,
)
from prototyping_inference_engine.unifier import (
    DisjunctivePieceUnifierAlgorithm,
)


class WithoutAggregationRewritingOperator(RewritingOperator):
    def __init__(self):
        self.disj_piece_unifier_algo = DisjunctivePieceUnifierAlgorithm()

    def rewrite(
        self,
        all_cqs: UnionQuery[ConjunctiveQuery],
        new_cqs: UnionQuery[ConjunctiveQuery],
        rules: set[Rule],
    ) -> UnionQuery[ConjunctiveQuery]:
        rewritten_cqs: set[ConjunctiveQuery] = set()
        disj_unifiers: set[DisjunctivePieceUnifier] = set()
        for rule in rules:
            disj_unifiers |= self.disj_piece_unifier_algo.compute_disjunctive_unifiers(
                all_cqs, new_cqs, rule
            )
        for disj_unifier in disj_unifiers:
            u = disj_unifier.associated_substitution
            new_cq_atoms = MutableAtomSet(u(list(disj_unifier.rule.body.atoms)))
            for piece_unifier in disj_unifier.piece_unifiers:
                new_cq_atoms |= u(list(piece_unifier.not_unified_part))
            rewritten_cqs.add(
                ConjunctiveQuery(
                    new_cq_atoms,
                    disj_unifier.query.answer_variables,
                    pre_substitution=Substitution(
                        {
                            v: u(v)
                            for v in disj_unifier.query.answer_variables
                            if v != u(v)
                        }
                    ),
                )
            )

        if rewritten_cqs:
            return UnionQuery(rewritten_cqs, all_cqs.answer_variables)

        return UnionQuery(answer_variables=all_cqs.answer_variables)
