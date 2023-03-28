from typing import Tuple, Type, Iterable

from api.atom.term.term import Term
from api.fact_base.fact_base import FactBase
from api.query.atomic_query import AtomicQuery
from api.query.conjunctive_query import ConjunctiveQuery

from api.query.query import Query
from api.substitution.substitution import Substitution
from query_processing.query_processing import QueryProcessing


class CSPQueryProcessing(QueryProcessing):
    def execute_query(self, target: FactBase, query: Query, sub: Substitution, filter_out_nulls: bool = True)\
            -> Iterable[tuple[Term]]:
        pass

    @classmethod
    def get_supported_query_types(cls) -> Tuple[Type[Query]]:
        return ConjunctiveQuery, AtomicQuery
