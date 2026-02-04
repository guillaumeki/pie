from abc import ABC, abstractmethod

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery


class RewritingOperator(ABC):
    @abstractmethod
    def rewrite(
        self,
        all_cqs: UnionQuery[ConjunctiveQuery],
        new_cqs: UnionQuery[ConjunctiveQuery],
        rules: set[Rule[ConjunctiveQuery, ConjunctiveQuery]],
    ) -> UnionQuery[ConjunctiveQuery]:
        pass

    def __call__(
        self,
        all_cqs: UnionQuery[ConjunctiveQuery],
        new_cqs: UnionQuery[ConjunctiveQuery],
        rules: set[Rule[ConjunctiveQuery, ConjunctiveQuery]],
    ) -> UnionQuery[ConjunctiveQuery]:
        return self.rewrite(all_cqs, new_cqs, rules)
