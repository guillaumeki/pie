from typing import Tuple, Type, Iterable

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.query.atomic_query import AtomicQuery
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery

from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.query_processing.query_processing import QueryProcessing


class CSPQueryProcessing(QueryProcessing):
    def execute_query(self, target: FactBase, query: Query, sub: Substitution, filter_out_nulls: bool = True)\
            -> Iterable[tuple[Term]]:
        pass

    @classmethod
    def get_supported_query_types(cls) -> Tuple[Type[Query]]:
        return ConjunctiveQuery, AtomicQuery
