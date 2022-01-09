from abc import abstractmethod
from typing import Iterable

from api.atom.term.term import Term
from api.fact_base.fact_base import FactBase
from api.query.query import Query
from api.query.query_support import QuerySupport


class QueryProcessing(QuerySupport):
    @abstractmethod
    def execute_query(self, target: FactBase, query: Query) -> Iterable[tuple[Term]]:
        pass
