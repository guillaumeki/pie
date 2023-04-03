from abc import ABC, abstractmethod

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries


class RewritingOperator(ABC):
    @abstractmethod
    def rewrite(self,
                all_cqs: UnionConjunctiveQueries,
                new_cqs: UnionConjunctiveQueries,
                rules: set[Rule[ConjunctiveQuery, ConjunctiveQuery]]) -> UnionConjunctiveQueries:
        pass

    def __call__(self,
                 all_cqs: UnionConjunctiveQueries,
                 new_cqs: UnionConjunctiveQueries,
                 rules: set[Rule[ConjunctiveQuery, ConjunctiveQuery]]) -> UnionConjunctiveQueries:
        return self.rewrite(all_cqs, new_cqs, rules)
