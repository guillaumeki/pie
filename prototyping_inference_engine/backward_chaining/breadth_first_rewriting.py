from functools import cache
from math import inf
from typing import Callable, Optional

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_union_conjunctive_queries import \
    RedundanciesCleanerUnionConjunctiveQueries
from prototyping_inference_engine.api.query.redundancies.ucq_redundancies_cleaner_provider import (
    UCQRedundanciesCleanerProvider, DefaultUCQRedundanciesCleanerProvider
)
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.backward_chaining.rewriting_operator.rewriting_operator import RewritingOperator
from prototyping_inference_engine.backward_chaining.rewriting_operator.rewriting_operator_provider import (
    RewritingOperatorProvider, DefaultRewritingOperatorProvider
)
from prototyping_inference_engine.backward_chaining.ucq_rewriting_algorithm import UcqRewritingAlgorithm


class BreadthFirstRewriting(UcqRewritingAlgorithm):
    def __init__(self,
                 rewriting_operator_provider: Optional[RewritingOperatorProvider] = None,
                 ucq_cleaner_provider: Optional[UCQRedundanciesCleanerProvider] = None):
        if ucq_cleaner_provider is None:
            ucq_cleaner_provider = DefaultUCQRedundanciesCleanerProvider()
        self._ucq_redundancies_cleaner: RedundanciesCleanerUnionConjunctiveQueries = ucq_cleaner_provider.get_cleaner()

        if rewriting_operator_provider is None:
            rewriting_operator_provider = DefaultRewritingOperatorProvider()
        self._rewriting_operator: RewritingOperator = rewriting_operator_provider.get_operator()

    @staticmethod
    @cache
    def instance() -> "BreadthFirstRewriting":
        return BreadthFirstRewriting()

    @staticmethod
    def _safe_renaming(ucq: UnionQuery[ConjunctiveQuery],
                       rule_set: set[Rule[ConjunctiveQuery, ConjunctiveQuery]]) -> UnionQuery[ConjunctiveQuery]:
        rules_variables = set(v for r in rule_set for v in r.variables)
        renaming = Substitution()
        for v in ucq.variables:
            if v in rules_variables:
                renaming[v] = Variable.fresh_variable()

        return renaming(ucq)

    def rewrite(self, ucq: UnionQuery[ConjunctiveQuery],
                rule_set: set[Rule[ConjunctiveQuery, ConjunctiveQuery]],
                step_limit: float = inf,
                verbose: bool = False,
                printer: Optional["Callable[[UnionQuery[ConjunctiveQuery], int], None]"] = None
                ) -> UnionQuery[ConjunctiveQuery]:
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
                if printer is None:
                    print(f"The UCQ produced at step {step} contains the following CQs:")
                    print(*ucq_result.conjunctive_queries, sep="\n")
                    print("------------")
                else:
                    printer(ucq_result, step)
        return ucq_result
