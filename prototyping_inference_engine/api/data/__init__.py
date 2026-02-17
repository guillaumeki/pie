"""
Data access abstractions for the inference engine.
"""

from typing import Any

from prototyping_inference_engine.api.data.comparison_data import ComparisonDataSource
from prototyping_inference_engine.api.data.functions.integraal_standard_functions import (
    IntegraalStandardFunctionSource,
)
from prototyping_inference_engine.api.data.python_function_data import (
    PythonFunctionReadable,
)
from prototyping_inference_engine.api.data.datalog_delegable import DatalogDelegable
from prototyping_inference_engine.api.data.delegating_atom_wrapper import DelAtomWrapper
from prototyping_inference_engine.api.data.queryable_data_del_atoms_wrapper import (
    QueryableDataDelAtomsWrapper,
)
from prototyping_inference_engine.api.data.collection.writable_readable_collection import (
    WritableReadableDataCollection,
)

__all__ = [
    "ComparisonDataSource",
    "IntegraalStandardFunctionSource",
    "PythonFunctionReadable",
    "DatalogDelegable",
    "DelAtomWrapper",
    "QueryableDataDelAtomsWrapper",
    "WritableReadableDataCollection",
    "InMemoryGraphStorage",
    "TripleStoreStorage",
    "RDBMSStore",
    "VirtualDeleteStorage",
    "StorageBuilder",
]


def __getattr__(name: str) -> Any:
    if name in {
        "InMemoryGraphStorage",
        "TripleStoreStorage",
        "RDBMSStore",
        "VirtualDeleteStorage",
        "StorageBuilder",
    }:
        from prototyping_inference_engine.api.data import storage as _storage

        return getattr(_storage, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
