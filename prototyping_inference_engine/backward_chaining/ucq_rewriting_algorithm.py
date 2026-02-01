from abc import ABC, abstractmethod
from typing import TypeVar

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.query.union_query import UnionQuery


BodyQueryType = TypeVar("BodyQueryType", bound=Query)
HeadQueryType = TypeVar("HeadQueryType", bound=Query)


class UcqRewritingAlgorithm(ABC):
    @abstractmethod
    def rewrite(self,
                ucq: UnionQuery[ConjunctiveQuery],
                rule_set: set[Rule[BodyQueryType, HeadQueryType]]) -> UnionQuery[ConjunctiveQuery]:
        pass
