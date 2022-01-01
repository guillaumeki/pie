from abc import ABC, abstractmethod, ABCMeta
from functools import cache
from typing import Tuple, List, Callable, FrozenSet, Type

from api.atom.term.term import Term
from api.query.query import Query


class UnsupportedFactBaseOperation(Exception):
    def __init__(self, operation, msg=None, *args):
        if not msg:
            msg = "The operation " + operation.__name__ + " is unsupported on this fact base"
        super().__init__(msg, *args)


def fact_base_operation(fun: Callable) -> Callable:
    fun.supported_operation = fun.__name__
    return fun


def fact_base_unsupported_operation(fun: Callable) -> Callable:
    def unsupported(*args, **kwargs):
        raise UnsupportedFactBaseOperation(fun, *args, **kwargs)

    unsupported.unsupported_operation = fun.__name__
    return unsupported


class MetaFactBase(ABCMeta):
    def __new__(mcs, clsname, bases, attrs):
        # We define constants that will contain the operations for this class and its subclasses
        attrs["_FACT_BASE_OPERATIONS"] = set()
        attrs["_SUPPORTED_FACT_BASE_OPERATIONS"] = set()

        # We look for already defined operations into the base classes
        for base in bases:
            for parent in base.mro():
                if hasattr(parent, "_FACT_BASE_OPERATIONS"):
                    attrs["_FACT_BASE_OPERATIONS"] |= getattr(parent, "_FACT_BASE_OPERATIONS")
                if hasattr(parent, "_SUPPORTED_FACT_BASE_OPERATIONS"):
                    attrs["_SUPPORTED_FACT_BASE_OPERATIONS"] |= getattr(parent, "_SUPPORTED_FACT_BASE_OPERATIONS")

        # We look for the operations defined by this class
        for attr_name in attrs:
            if callable(attrs[attr_name]):
                # If a decorator fact_base_operation was used
                if hasattr(attrs[attr_name], "supported_operation"):
                    attrs["_FACT_BASE_OPERATIONS"].add(attrs[attr_name].supported_operation)
                    attrs["_SUPPORTED_FACT_BASE_OPERATIONS"].add(attrs[attr_name].supported_operation)
                # Else if a decorator fact_base_unsupported_operation was used
                elif hasattr(attrs[attr_name], "unsupported_operation"):
                    attrs["_FACT_BASE_OPERATIONS"].add(attrs[attr_name].unsupported_operation)
                # Else if an already defined operation was implemented
                elif attrs[attr_name].__name__ in attrs["_FACT_BASE_OPERATIONS"]:
                    attrs["_SUPPORTED_FACT_BASE_OPERATIONS"].add(attrs[attr_name].__name__)

        return super(MetaFactBase, mcs).__new__(mcs, clsname, bases, attrs)


class FactBase(ABC):
    _FACT_BASE_OPERATIONS = set()
    _SUPPORTED_FACT_BASE_OPERATIONS = set()

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

    @abstractmethod
    def execute_query(self, query: Query) -> List[Tuple[Term]]:
        pass

    @classmethod
    @cache
    def get_supported_operations(cls) -> FrozenSet[str]:
        return frozenset(cls._SUPPORTED_FACT_BASE_OPERATIONS)

    @classmethod
    @cache
    def get_all_operations(cls) -> FrozenSet[str]:
        return frozenset(cls._FACT_BASE_OPERATIONS)

    @fact_base_unsupported_operation
    def get_variables(self):
        pass

    @fact_base_unsupported_operation
    def get_constants(self):
        pass

    @fact_base_unsupported_operation
    def get_terms(self):
        pass
