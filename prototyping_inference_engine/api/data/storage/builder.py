"""Storage builder for in-memory, triple-store, and RDBMS backends."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rdflib import Graph

from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)
from prototyping_inference_engine.api.data.storage.rdbms.drivers import (
    HSQLDBDriver,
    MySQLDriver,
    PostgreSQLDriver,
    RDBMSDriver,
    SQLiteDriver,
)
from prototyping_inference_engine.api.data.storage.rdbms.layouts import (
    AdHocSQLLayout,
    EncodingAdHocSQLLayout,
    NaturalSQLLayout,
    RDBMSStorageLayout,
)
from prototyping_inference_engine.api.data.storage.rdbms_store import RDBMSStore
from prototyping_inference_engine.api.data.storage.triple_store_storage import (
    TripleStoreStorage,
)


class StorageKind(Enum):
    GRAPH = "graph"
    TRIPLE = "triple"
    RDBMS = "rdbms"


@dataclass
class StorageBuilder:
    """Builder inspired by Integraal's storage builder, with decoupled concerns."""

    _kind: StorageKind = StorageKind.GRAPH
    _sqlite_path: str | None = None
    _rdbms_driver: RDBMSDriver | None = None
    _layout: RDBMSStorageLayout | None = None
    _triple_graph: Graph | None = None

    @staticmethod
    def default_builder() -> "StorageBuilder":
        return StorageBuilder()

    @staticmethod
    def default_storage() -> ReadableData:
        return InMemoryGraphStorage()

    def use_in_memory_graph_store(self) -> "StorageBuilder":
        self._kind = StorageKind.GRAPH
        return self

    def use_triple_store(self, graph: Graph | None = None) -> "StorageBuilder":
        self._kind = StorageKind.TRIPLE
        self._triple_graph = graph
        return self

    def use_sqlite_db(self, path: str) -> "StorageBuilder":
        self._kind = StorageKind.RDBMS
        self._sqlite_path = path
        self._rdbms_driver = SQLiteDriver.from_path(path)
        return self

    def use_postgresql_db(self, dsn: str) -> "StorageBuilder":
        self._kind = StorageKind.RDBMS
        self._rdbms_driver = PostgreSQLDriver.from_dsn(dsn)
        return self

    def use_mysql_db(self, **params: object) -> "StorageBuilder":
        self._kind = StorageKind.RDBMS
        self._rdbms_driver = MySQLDriver.from_params(**params)
        return self

    def use_hsqldb(
        self, jdbc_url: str, user: str = "sa", password: str = ""
    ) -> "StorageBuilder":
        self._kind = StorageKind.RDBMS
        self._rdbms_driver = HSQLDBDriver.from_jdbc(
            jdbc_url, user=user, password=password
        )
        return self

    def use_adhoc_sql_layout(self) -> "StorageBuilder":
        self._layout = AdHocSQLLayout()
        return self

    def use_encoding_adhoc_sql_layout(self) -> "StorageBuilder":
        self._layout = EncodingAdHocSQLLayout()
        return self

    def use_natural_sql_layout(self, layout: NaturalSQLLayout) -> "StorageBuilder":
        self._layout = layout
        return self

    def build(self) -> ReadableData:
        if self._kind == StorageKind.GRAPH:
            return InMemoryGraphStorage()
        if self._kind == StorageKind.TRIPLE:
            return TripleStoreStorage(graph=self._triple_graph)

        if self._rdbms_driver is None:
            if self._sqlite_path is None:
                self._sqlite_path = ":memory:"
            self._rdbms_driver = SQLiteDriver.from_path(self._sqlite_path)

        layout = self._layout if self._layout is not None else EncodingAdHocSQLLayout()
        return RDBMSStore(driver=self._rdbms_driver, layout=layout)
