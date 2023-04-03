from abc import ABC, abstractmethod
from typing import Tuple, Type

from prototyping_inference_engine.api.query.query import Query


class QuerySupport(ABC):
    @classmethod
    @abstractmethod
    def get_supported_query_types(cls) -> Tuple[Type[Query]]:
        pass

    @classmethod
    def is_query_type_supported(cls, query_type: Type[Query]) -> bool:
        for sqt in cls.get_supported_query_types():
            if issubclass(query_type, sqt):
                return True
        return False

    @classmethod
    def is_query_supported(cls, query: Query) -> bool:
        return cls.is_query_type_supported(type(query))
