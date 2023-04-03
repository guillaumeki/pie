from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.backward_chaining.rewriting_operator.rewriting_operator import RewritingOperator
from prototyping_inference_engine.backward_chaining.unifier.disjunctive_piece_unifier import DisjunctivePieceUnifier
from prototyping_inference_engine.backward_chaining.unifier.disjunctive_piece_unifier_algorithm import DisjunctivePieceUnifierAlgorithm


class WithoutAggregationRewritingOperator(RewritingOperator):
    def __init__(self):
        self.disj_piece_unifier_algo = DisjunctivePieceUnifierAlgorithm()

    def rewrite(self,
                all_cqs: UnionConjunctiveQueries,
                new_cqs: UnionConjunctiveQueries,
                rules: set[Rule[ConjunctiveQuery, ConjunctiveQuery]]) -> UnionConjunctiveQueries:
        rewritten_cqs: set[ConjunctiveQuery] = set()
        disj_unifiers: set[DisjunctivePieceUnifier] = set()
        for rule in rules:
            disj_unifiers |= self.disj_piece_unifier_algo.compute_disjunctive_unifiers(all_cqs, new_cqs, rule)
        for disj_unifier in disj_unifiers:
            u = disj_unifier.associated_substitution
            new_cq_atoms = MutableAtomSet(u(disj_unifier.rule.body.atoms))
            for piece_unifier in disj_unifier.piece_unifiers:
                new_cq_atoms |= u(piece_unifier.not_unified_part)
            rewritten_cqs.add(ConjunctiveQuery(
                new_cq_atoms,
                disj_unifier.query.answer_variables,
                pre_substitution=Substitution({v: u(v) for v in disj_unifier.query.answer_variables if v != u(v)})))

        if rewritten_cqs:
            return UnionConjunctiveQueries(rewritten_cqs, all_cqs.answer_variables)

        return UnionConjunctiveQueries(answer_variables=all_cqs.answer_variables)
