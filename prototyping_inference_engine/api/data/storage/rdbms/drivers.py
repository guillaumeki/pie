"""RDBMS driver abstractions and implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol


class DBConnection(Protocol):
    def cursor(self): ...

    def commit(self) -> None: ...

    def close(self) -> None: ...


@dataclass(frozen=True)
class RDBMSDriver:
    """Database driver abstraction used by RDBMS storage."""

    name: str
    connector: Callable[..., DBConnection]
    connect_kwargs: dict[str, Any]

    def connect(self) -> DBConnection:
        return self.connector(**self.connect_kwargs)


@dataclass(frozen=True)
class SQLiteDriver(RDBMSDriver):
    @staticmethod
    def from_path(path: str) -> "SQLiteDriver":
        import sqlite3

        return SQLiteDriver(
            name="sqlite",
            connector=sqlite3.connect,
            connect_kwargs={"database": path},
        )


@dataclass(frozen=True)
class PostgreSQLDriver(RDBMSDriver):
    @staticmethod
    def from_dsn(dsn: str) -> "PostgreSQLDriver":
        if dsn.startswith("postgresql+"):
            scheme_end = dsn.find("://")
            if scheme_end != -1:
                dsn = "postgresql" + dsn[scheme_end:]
        try:
            import psycopg  # type: ignore[import-not-found,import-untyped]
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("psycopg is required for PostgreSQLDriver") from exc

        return PostgreSQLDriver(
            name="postgresql",
            connector=psycopg.connect,
            connect_kwargs={"conninfo": dsn},
        )


@dataclass(frozen=True)
class MySQLDriver(RDBMSDriver):
    @staticmethod
    def from_params(**params: Any) -> "MySQLDriver":
        try:
            import pymysql  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("pymysql is required for MySQLDriver") from exc

        return MySQLDriver(
            name="mysql",
            connector=pymysql.connect,
            connect_kwargs=params,
        )


@dataclass(frozen=True)
class HSQLDBDriver(RDBMSDriver):
    @staticmethod
    def from_jdbc(url: str, user: str = "sa", password: str = "") -> "HSQLDBDriver":
        try:
            import jaydebeapi  # type: ignore[import-not-found,import-untyped]
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("jaydebeapi is required for HSQLDBDriver") from exc

        return HSQLDBDriver(
            name="hsqldb",
            connector=jaydebeapi.connect,
            connect_kwargs={
                "jclassname": "org.hsqldb.jdbcDriver",
                "url": url,
                "driver_args": [user, password],
            },
        )
