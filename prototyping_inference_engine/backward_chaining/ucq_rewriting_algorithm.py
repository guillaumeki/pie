from abc import ABC, abstractmethod
from math import inf
from typing import Callable, Optional

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery


class UcqRewritingAlgorithm(ABC):
    @abstractmethod
    def rewrite(
        self,
        ucq: UnionQuery[ConjunctiveQuery],
        rule_set: set[Rule[ConjunctiveQuery, ConjunctiveQuery]],
        step_limit: float = inf,
        verbose: bool = False,
        printer: Optional[Callable[[UnionQuery[ConjunctiveQuery], int], None]] = None,
    ) -> UnionQuery[ConjunctiveQuery]:
        pass
