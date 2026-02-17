"""RDBMS storage layouts."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Protocol, Sequence

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.schema import (
    LogicalType,
    PositionSpec,
    RelationSchema,
)
from prototyping_inference_engine.api.data.storage.acceptance import AcceptanceResult


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", value)


@dataclass(frozen=True)
class TableSpec:
    """Explicit mapping used by NaturalSQLLayout."""

    table: str
    columns: tuple[str, ...]
    column_types: tuple[LogicalType, ...] | None = None
    nullable: tuple[bool, ...] | None = None


@dataclass(frozen=True)
class SelectPlan:
    sql: str
    params: tuple[object, ...]
    answer_positions: tuple[int, ...]


class RDBMSStorageLayout(Protocol):
    def accepts_predicate(self, predicate: Predicate) -> AcceptanceResult: ...

    def accepts_atom(self, atom: Atom) -> AcceptanceResult: ...

    def ensure_schema(self, cursor, predicate: Predicate) -> None: ...

    def insert_sql(self, atom: Atom) -> tuple[str, tuple[object, ...]]: ...

    def delete_sql(self, atom: Atom) -> tuple[str, tuple[object, ...]]: ...

    def select_sql(self, query: BasicQuery) -> SelectPlan: ...

    def known_predicates(self) -> Iterable[Predicate]: ...

    def get_schema(self, predicate: Predicate) -> RelationSchema | None: ...

    def get_schemas(self) -> Iterable[RelationSchema]: ...

    def bind(self, connection, driver_name: str) -> None: ...


class _BaseDynamicLayout:
    def __init__(self) -> None:
        self._known_predicates: set[Predicate] = set()

    def known_predicates(self) -> Iterable[Predicate]:
        return tuple(self._known_predicates)

    def bind(self, connection, driver_name: str) -> None:
        return None

    def accepts_predicate(self, predicate: Predicate) -> AcceptanceResult:
        return AcceptanceResult.ok()

    def accepts_atom(self, atom: Atom) -> AcceptanceResult:
        return self.accepts_predicate(atom.predicate)

    def get_schema(self, predicate: Predicate) -> RelationSchema | None:
        if predicate not in self._known_predicates:
            return None
        positions = tuple(
            PositionSpec(name=f"c{idx}", logical_type=LogicalType.UNKNOWN)
            for idx in range(predicate.arity)
        )
        return RelationSchema(predicate, positions)

    def get_schemas(self) -> Iterable[RelationSchema]:
        for predicate in self._known_predicates:
            schema = self.get_schema(predicate)
            if schema is not None:
                yield schema

    def _column_names(self, predicate: Predicate) -> tuple[str, ...]:
        return tuple(f"c{idx}" for idx in range(predicate.arity))

    def _create_table(self, cursor, table: str, columns: Sequence[str]) -> None:
        cols = ", ".join(f"{c} TEXT NOT NULL" for c in columns)
        pk = ", ".join(columns)
        sql = f"CREATE TABLE IF NOT EXISTS {table} ({cols}, PRIMARY KEY ({pk}))"
        cursor.execute(sql)

    def ensure_schema(self, cursor, predicate: Predicate) -> None:
        self._create_table(
            cursor, self._table_name(predicate), self._column_names(predicate)
        )
        self._known_predicates.add(predicate)

    def insert_sql(self, atom: Atom) -> tuple[str, tuple[object, ...]]:
        table = self._table_name(atom.predicate)
        columns = self._column_names(atom.predicate)
        placeholders = ", ".join("?" for _ in columns)
        sql = (
            f"INSERT OR IGNORE INTO {table} ({', '.join(columns)}) "
            f"VALUES ({placeholders})"
        )
        params = tuple(str(t.identifier) for t in atom.terms)
        return sql, params

    def delete_sql(self, atom: Atom) -> tuple[str, tuple[object, ...]]:
        table = self._table_name(atom.predicate)
        columns = self._column_names(atom.predicate)
        where = " AND ".join(f"{c} = ?" for c in columns)
        # table/column identifiers come from sanitized/generated predicate mappings.
        sql = f"DELETE FROM {table} WHERE {where}"  # nosec B608
        params = tuple(str(t.identifier) for t in atom.terms)
        return sql, params

    def select_sql(self, query: BasicQuery) -> SelectPlan:
        table = self._table_name(query.predicate)
        columns = self._column_names(query.predicate)
        where_parts: list[str] = []
        params: list[object] = []
        for pos, term in sorted(query.bound_positions.items()):
            where_parts.append(f"{columns[pos]} = ?")
            params.append(str(term.identifier))
        answer_positions = tuple(sorted(query.answer_variables.keys()))
        select_columns = ", ".join(columns[pos] for pos in answer_positions)
        if not select_columns:
            select_columns = "1"
        # table/column identifiers come from sanitized/generated predicate mappings.
        sql = f"SELECT {select_columns} FROM {table}"  # nosec B608
        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)
        return SelectPlan(
            sql=sql, params=tuple(params), answer_positions=answer_positions
        )

    def _table_name(self, predicate: Predicate) -> str:
        raise NotImplementedError


class AdHocSQLLayout(_BaseDynamicLayout):
    """One relation per predicate with sanitized names."""

    def _table_name(self, predicate: Predicate) -> str:
        return f"p_{_safe_name(predicate.name)}_{predicate.arity}"


class EncodingAdHocSQLLayout(_BaseDynamicLayout):
    """Ad-hoc layout with encoded predicate names."""

    @staticmethod
    def _encode(name: str) -> str:
        payload = base64.urlsafe_b64encode(name.encode("utf-8")).decode("ascii")
        return payload.rstrip("=")

    def _table_name(self, predicate: Predicate) -> str:
        return f"pe_{self._encode(predicate.name)}_{predicate.arity}"


class NaturalSQLLayout:
    """Layout where table and columns are explicitly provided per predicate."""

    def __init__(
        self,
        mapping: Mapping[Predicate, TableSpec] | None = None,
        auto_discover: bool = True,
    ):
        self._mapping = dict(mapping or {})
        self._auto_discover = auto_discover
        self._connection = None
        self._driver_name = ""
        self._discovered = False

    def bind(self, connection, driver_name: str) -> None:
        self._connection = connection
        self._driver_name = driver_name

    @staticmethod
    def _logical_type_from_decl(decl: str | None) -> LogicalType:
        if decl is None:
            return LogicalType.UNKNOWN
        lowered = decl.lower()
        if "int" in lowered:
            return LogicalType.INTEGER
        if "float" in lowered or "double" in lowered or "real" in lowered:
            return LogicalType.FLOAT
        if "bool" in lowered:
            return LogicalType.BOOLEAN
        if "char" in lowered or "text" in lowered or "str" in lowered:
            return LogicalType.STRING
        return LogicalType.UNKNOWN

    def _discover_if_needed(self) -> None:
        if self._discovered or not self._auto_discover:
            return
        if self._mapping:
            self._discovered = True
            return
        if self._connection is None:
            return

        cursor = self._connection.cursor()
        try:
            if self._driver_name == "sqlite":
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                table_names = [row[0] for row in cursor.fetchall()]
                for table in table_names:
                    cursor.execute(f"PRAGMA table_info({table})")
                    rows = cursor.fetchall()
                    if not rows:
                        continue
                    columns = tuple(row[1] for row in rows)
                    types = tuple(self._logical_type_from_decl(row[2]) for row in rows)
                    nullable = tuple(row[3] == 0 for row in rows)
                    predicate = Predicate(table, len(columns))
                    self._mapping[predicate] = TableSpec(
                        table=table,
                        columns=columns,
                        column_types=types,
                        nullable=nullable,
                    )
            else:
                cursor.execute(
                    "SELECT table_name, column_name, data_type, is_nullable "
                    "FROM information_schema.columns ORDER BY table_name, ordinal_position"
                )
                grouped: dict[str, list[tuple[str, str | None, bool]]] = {}
                for table, column, data_type, is_nullable in cursor.fetchall():
                    grouped.setdefault(table, []).append(
                        (column, data_type, str(is_nullable).upper() == "YES")
                    )
                for table, specs in grouped.items():
                    columns = tuple(s[0] for s in specs)
                    types = tuple(self._logical_type_from_decl(s[1]) for s in specs)
                    nullable = tuple(s[2] for s in specs)
                    predicate = Predicate(table, len(columns))
                    self._mapping[predicate] = TableSpec(
                        table=table,
                        columns=columns,
                        column_types=types,
                        nullable=nullable,
                    )
        except Exception:
            # Discovery is best-effort and should not break store construction.
            pass
        finally:
            self._discovered = True

    def known_predicates(self) -> Iterable[Predicate]:
        self._discover_if_needed()
        return tuple(self._mapping.keys())

    def accepts_predicate(self, predicate: Predicate) -> AcceptanceResult:
        self._discover_if_needed()
        spec = self._mapping.get(predicate)
        if spec is None:
            return AcceptanceResult.reject(f"Predicate {predicate} is not mapped")
        if len(spec.columns) != predicate.arity:
            return AcceptanceResult.reject(
                f"Predicate {predicate} arity mismatch with table mapping"
            )
        return AcceptanceResult.ok()

    def accepts_atom(self, atom: Atom) -> AcceptanceResult:
        return self.accepts_predicate(atom.predicate)

    def ensure_schema(self, cursor, predicate: Predicate) -> None:
        acceptance = self.accepts_predicate(predicate)
        if not acceptance.accepted:
            raise ValueError(acceptance.reason)

    def _spec(self, predicate: Predicate) -> TableSpec:
        self._discover_if_needed()
        spec = self._mapping.get(predicate)
        if spec is None:
            raise ValueError(f"Predicate {predicate} is not mapped")
        return spec

    def get_schema(self, predicate: Predicate) -> RelationSchema | None:
        self._discover_if_needed()
        spec = self._mapping.get(predicate)
        if spec is None:
            return None
        types = (
            spec.column_types
            if spec.column_types is not None
            else tuple(LogicalType.UNKNOWN for _ in spec.columns)
        )
        nullable = (
            spec.nullable
            if spec.nullable is not None
            else tuple(False for _ in spec.columns)
        )
        positions = tuple(
            PositionSpec(name=column, logical_type=types[idx], nullable=nullable[idx])
            for idx, column in enumerate(spec.columns)
        )
        return RelationSchema(predicate, positions)

    def get_schemas(self) -> Iterable[RelationSchema]:
        self._discover_if_needed()
        for predicate in self._mapping:
            schema = self.get_schema(predicate)
            if schema is not None:
                yield schema

    def insert_sql(self, atom: Atom) -> tuple[str, tuple[object, ...]]:
        spec = self._spec(atom.predicate)
        placeholders = ", ".join("?" for _ in spec.columns)
        sql = (
            f"INSERT OR IGNORE INTO {spec.table} ({', '.join(spec.columns)}) "
            f"VALUES ({placeholders})"
        )
        params = tuple(str(t.identifier) for t in atom.terms)
        return sql, params

    def delete_sql(self, atom: Atom) -> tuple[str, tuple[object, ...]]:
        spec = self._spec(atom.predicate)
        where = " AND ".join(f"{c} = ?" for c in spec.columns)
        # table/column identifiers come from explicit validated TableSpec mapping.
        sql = f"DELETE FROM {spec.table} WHERE {where}"  # nosec B608
        params = tuple(str(t.identifier) for t in atom.terms)
        return sql, params

    def select_sql(self, query: BasicQuery) -> SelectPlan:
        spec = self._spec(query.predicate)
        where_parts: list[str] = []
        params: list[object] = []
        for pos, term in sorted(query.bound_positions.items()):
            where_parts.append(f"{spec.columns[pos]} = ?")
            params.append(str(term.identifier))
        answer_positions = tuple(sorted(query.answer_variables.keys()))
        select_columns = ", ".join(spec.columns[pos] for pos in answer_positions)
        if not select_columns:
            select_columns = "1"
        # table/column identifiers come from explicit validated TableSpec mapping.
        sql = f"SELECT {select_columns} FROM {spec.table}"  # nosec B608
        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)
        return SelectPlan(
            sql=sql, params=tuple(params), answer_positions=answer_positions
        )
