from typing import Type, Tuple, List

from api.atom.term.term import Term
from api.fact_base.fact_base import FactBase
from api.query.atomic_query import AtomicQuery
from api.query.query import Query


class MutableFactBase(FactBase):
    @classmethod
    def get_supported_query_types(cls) -> Tuple[Type[Query]]:
        return AtomicQuery,
