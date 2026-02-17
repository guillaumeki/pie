"""RDBMS-backed storage with pluggable layout and driver."""

from __future__ import annotations

from contextlib import closing
from typing import Iterable, Iterator, Set

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.atomic_pattern import UnconstrainedPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.schema import RelationSchema, SchemaAware
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.data.storage.acceptance import AcceptanceResult
from prototyping_inference_engine.api.data.storage.protocols import AtomAcceptance
from prototyping_inference_engine.api.data.storage.rdbms.drivers import RDBMSDriver
from prototyping_inference_engine.api.data.storage.rdbms.layouts import (
    RDBMSStorageLayout,
)
from prototyping_inference_engine.api.fact_base.protocols import Writable


class RDBMSStore(FactBase, Writable, AtomAcceptance, SchemaAware):
    """Storage implementation backed by an SQL database."""

    def __init__(self, driver: RDBMSDriver, layout: RDBMSStorageLayout):
        self._driver = driver
        self._layout = layout
        self._connection = self._driver.connect()
        self._layout.bind(self._connection, self._driver.name)

    def _adapt_placeholders(self, sql: str) -> str:
        if self._driver.name in {"postgresql", "mysql"}:
            return sql.replace("?", "%s")
        return sql

    def _adapt_insert_sql(self, sql: str) -> str:
        if self._driver.name == "postgresql":
            prefix = "INSERT OR IGNORE INTO "
            if sql.startswith(prefix):
                sql = "INSERT INTO " + sql[len(prefix) :]
                sql += " ON CONFLICT DO NOTHING"
            return sql
        if self._driver.name == "mysql":
            prefix = "INSERT OR IGNORE INTO "
            if sql.startswith(prefix):
                sql = "INSERT IGNORE INTO " + sql[len(prefix) :]
            return sql
        return sql

    def close(self) -> None:
        self._connection.close()

    def accepts_predicate(self, predicate: Predicate) -> AcceptanceResult:
        return self._layout.accepts_predicate(predicate)

    def accepts_atom(self, atom: Atom) -> AcceptanceResult:
        if any(isinstance(term, Variable) for term in atom.terms):
            return AcceptanceResult.reject("RDBMS storage does not accept variables")
        return self._layout.accepts_atom(atom)

    def get_predicates(self) -> Iterator[Predicate]:
        return iter(set(self._layout.known_predicates()))

    def has_predicate(self, predicate: Predicate) -> bool:
        return any(p == predicate for p in self._layout.known_predicates())

    def get_atomic_pattern(self, predicate: Predicate) -> UnconstrainedPattern:
        return UnconstrainedPattern(predicate)

    def get_schema(self, predicate: Predicate) -> RelationSchema | None:
        return self._layout.get_schema(predicate)

    def get_schemas(self) -> Iterable[RelationSchema]:
        return self._layout.get_schemas()

    def can_evaluate(self, query: BasicQuery) -> bool:
        return self.accepts_predicate(query.predicate).accepted

    def evaluate(self, query: BasicQuery) -> Iterator[tuple[Term, ...]]:
        acceptance = self.accepts_predicate(query.predicate)
        if not acceptance.accepted:
            raise ValueError(acceptance.reason)

        plan = self._layout.select_sql(query)
        sql = self._adapt_placeholders(plan.sql)
        with closing(self._connection.cursor()) as cursor:
            cursor.execute(sql, plan.params)
            rows = cursor.fetchall()

        if not plan.answer_positions:
            for _ in rows:
                yield tuple()
            return

        for row in rows:
            yield tuple(Constant(value) for value in row)

    @property
    def variables(self) -> Set[Variable]:
        return set()

    @property
    def constants(self) -> Set[Constant]:
        constants: Set[Constant] = set()
        for atom in self:
            constants.update(atom.constants)
        return constants

    @property
    def terms(self) -> Set[Term]:
        terms: Set[Term] = set()
        for atom in self:
            terms.update(atom.terms)
        return terms

    def add(self, atom: Atom) -> None:
        acceptance = self.accepts_atom(atom)
        if not acceptance.accepted:
            raise ValueError(acceptance.reason)

        with closing(self._connection.cursor()) as cursor:
            self._layout.ensure_schema(cursor, atom.predicate)
            sql, params = self._layout.insert_sql(atom)
            sql = self._adapt_placeholders(sql)
            sql = self._adapt_insert_sql(sql)
            cursor.execute(sql, params)
        self._connection.commit()

    def update(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.add(atom)

    def remove(self, atom: Atom) -> None:
        acceptance = self.accepts_atom(atom)
        if not acceptance.accepted:
            return
        with closing(self._connection.cursor()) as cursor:
            self._layout.ensure_schema(cursor, atom.predicate)
            sql, params = self._layout.delete_sql(atom)
            sql = self._adapt_placeholders(sql)
            cursor.execute(sql, params)
        self._connection.commit()

    def remove_all(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.remove(atom)

    def __iter__(self) -> Iterator[Atom]:
        for predicate in self._layout.known_predicates():
            query = BasicQuery(
                predicate=predicate,
                bound_positions={},
                answer_variables={
                    pos: Variable(f"V{pos}") for pos in range(predicate.arity)
                },
            )
            for row in self.evaluate(query):
                yield Atom(predicate, *row)

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __contains__(self, atom: Atom) -> bool:
        query = BasicQuery(
            predicate=atom.predicate,
            bound_positions={pos: term for pos, term in enumerate(atom.terms)},
            answer_variables={},
        )
        return any(True for _ in self.evaluate(query))
