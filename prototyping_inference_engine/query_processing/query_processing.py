from abc import abstractmethod
from typing import Iterable

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.query.query_support import QuerySupport


class QueryProcessing(QuerySupport):
    @abstractmethod
    def execute_query(self, target: FactBase, query: Query) -> Iterable[tuple[Term]]:
        pass
