from functools import cache
from math import inf

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_union_conjunctive_queries import \
    RedundanciesCleanerUnionConjunctiveQueries
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.backward_chaining.rewriting_operator.rewriting_operator import RewritingOperator
from prototyping_inference_engine.backward_chaining.rewriting_operator.without_aggregation_rewriting_operator import \
    WithoutAggregationRewritingOperator
from prototyping_inference_engine.backward_chaining.ucq_rewriting_algorithm import UcqRewritingAlgorithm


class BreadthFirstRewriting(UcqRewritingAlgorithm):
    def __init__(self,
                 rewriting_operator: RewritingOperator = None,
                 ucq_redundancies_cleaner: RedundanciesCleanerUnionConjunctiveQueries = None):
        if ucq_redundancies_cleaner:
            self._ucq_redundancies_cleaner: RedundanciesCleanerUnionConjunctiveQueries = ucq_redundancies_cleaner
        else:
            self._ucq_redundancies_cleaner: RedundanciesCleanerUnionConjunctiveQueries\
                = RedundanciesCleanerUnionConjunctiveQueries.instance()

        if rewriting_operator:
            self._rewriting_operator: RewritingOperator = rewriting_operator
        else:
            self._rewriting_operator: RewritingOperator = WithoutAggregationRewritingOperator()

    @staticmethod
    @cache
    def instance(
            rewriting_operator: RewritingOperator = None,
            ucq_redundancies_cleaner: RedundanciesCleanerUnionConjunctiveQueries = None) \
            -> "BreadthFirstRewriting":
        return BreadthFirstRewriting(rewriting_operator, ucq_redundancies_cleaner)

    @staticmethod
    def _safe_renaming(ucq: UnionConjunctiveQueries,
                       rule_set: set[Rule[ConjunctiveQuery, ConjunctiveQuery]]) -> UnionConjunctiveQueries:
        rules_variables = set(v for r in rule_set for v in r.variables)
        renaming = Substitution()
        for v in ucq.variables:
            if v in rules_variables:
                renaming[v] = Variable.fresh_variable()

        return renaming(ucq)

    def rewrite(self, ucq: UnionConjunctiveQueries,
                rule_set: set[Rule[ConjunctiveQuery, ConjunctiveQuery]],
                step_limit: int = inf,
                verbose: bool = False) -> UnionConjunctiveQueries:
        ucq = self._safe_renaming(ucq, rule_set)
        ucq_new = self._ucq_redundancies_cleaner.compute_cover(ucq)
        ucq_result = ucq_new
        step = 0
        while ucq_new.conjunctive_queries and step < step_limit:
            step += 1
            ucq_new = self._rewriting_operator(ucq_result, ucq_new, rule_set)
            ucq_new = self._ucq_redundancies_cleaner.compute_cover(ucq_new)
            ucq_new = self._ucq_redundancies_cleaner.remove_more_specific_than(ucq_new, ucq_result)
            ucq_result = self._ucq_redundancies_cleaner.remove_more_specific_than(ucq_result, ucq_new)
            ucq_result |= ucq_new
            if verbose:
                print(f"The UCQ produced at step {step} contains the following CQs:")
                print(*ucq_result.conjunctive_queries, sep="\n")
                print("------------")
        return ucq_result
