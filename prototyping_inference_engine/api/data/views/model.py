"""View declaration model objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class DatasourceProtocol(Enum):
    """Known datasource protocols for view declarations."""

    POSTGRESQL = "PostgreSQL"
    MYSQL = "MySQL"
    SQLITE = "SQLite"
    HSQLDB = "HSQLDB"
    MONGODB = "MongoDB"
    SPARQL_ENDPOINT = "SparqlEndpoint"
    JSON_WEB_API = "JSONWebApi"

    @classmethod
    def from_label(cls, label: str) -> "DatasourceProtocol | None":
        normalized = label.strip().lower()
        by_label = {
            "postgresql": cls.POSTGRESQL,
            "mysql": cls.MYSQL,
            "sqlite": cls.SQLITE,
            "hsqldb": cls.HSQLDB,
            "mongodb": cls.MONGODB,
            "sparqlendpoint": cls.SPARQL_ENDPOINT,
            "sparql_endpoint": cls.SPARQL_ENDPOINT,
            "jsonwebapi": cls.JSON_WEB_API,
            "json_web_api": cls.JSON_WEB_API,
        }
        return by_label.get(normalized)


class MissingValuePolicy(Enum):
    """Policy used to interpret missing values in view tuples."""

    IGNORE = "IGNORE"
    FREEZE = "FREEZE"
    EXIST = "EXIST"
    OPTIONAL = "OPTIONAL"

    @classmethod
    def from_label(cls, label: str) -> "MissingValuePolicy | None":
        normalized = label.strip().upper()
        by_label = {
            "IGNORE": cls.IGNORE,
            "FREEZE": cls.FREEZE,
            "EXIST": cls.EXIST,
            "OPTIONAL": cls.OPTIONAL,
        }
        return by_label.get(normalized)


@dataclass(frozen=True)
class ViewAttributeSpec:
    """Signature-level attribute options for a view position."""

    mandatory: str | None = None
    if_missing: MissingValuePolicy = MissingValuePolicy.FREEZE
    selection: str | None = None

    @property
    def is_mandatory(self) -> bool:
        return self.mandatory is not None


@dataclass(frozen=True)
class DatasourceDeclaration:
    """Datasource declaration from a view document."""

    id: str
    protocol: str
    parameters: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ViewDeclaration:
    """Single relational view declaration."""

    id: str
    datasource: str
    signature: tuple[ViewAttributeSpec, ...]
    query: str | None = None
    query_file: str | None = None
    position: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    @property
    def arity(self) -> int:
        return len(self.signature)


@dataclass(frozen=True)
class ViewDocument:
    """Complete view declaration document."""

    datasources: tuple[DatasourceDeclaration, ...]
    views: tuple[ViewDeclaration, ...]
