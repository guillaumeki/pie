import sqlite3
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.rdbms.drivers import (
    RDBMSDriver,
    SQLiteDriver,
)
from prototyping_inference_engine.api.data.storage.rdbms.layouts import AdHocSQLLayout
from prototyping_inference_engine.api.data.storage.rdbms_store import RDBMSStore


class _NamedSQLiteDriver(RDBMSDriver):
    @staticmethod
    def named(name: str) -> "_NamedSQLiteDriver":
        return _NamedSQLiteDriver(
            name=name,
            connector=sqlite3.connect,
            connect_kwargs={"database": ":memory:"},
        )


class TestRDBMSStoreBranches(unittest.TestCase):
    def test_sql_adaptation_branches(self):
        store_pg = RDBMSStore(_NamedSQLiteDriver.named("postgresql"), AdHocSQLLayout())
        self.assertEqual(store_pg._adapt_placeholders("a ? b ?"), "a %s b %s")
        self.assertIn(
            "ON CONFLICT DO NOTHING",
            store_pg._adapt_insert_sql("INSERT OR IGNORE INTO t (a) VALUES (?)"),
        )
        store_pg.close()

        store_my = RDBMSStore(_NamedSQLiteDriver.named("mysql"), AdHocSQLLayout())
        self.assertEqual(
            store_my._adapt_insert_sql("INSERT OR IGNORE INTO t (a) VALUES (?)"),
            "INSERT IGNORE INTO t (a) VALUES (?)",
        )
        store_my.close()

    def test_basic_methods_and_empty_answer_positions(self):
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), AdHocSQLLayout())
        p = Predicate("p", 2)
        atom = Atom(p, Constant("a"), Constant("b"))
        store.add(atom)

        self.assertTrue(store.accepts_predicate(p).accepted)
        self.assertTrue(store.has_predicate(p))
        self.assertIn(p, set(store.get_predicates()))
        self.assertTrue(store.can_evaluate(BasicQuery(p, {}, {0: Variable("X")})))

        query_full_bound = BasicQuery(p, {0: Constant("a"), 1: Constant("b")}, {})
        self.assertEqual(list(store.evaluate(query_full_bound)), [tuple()])

        pattern = store.get_atomic_pattern(p)
        self.assertEqual(pattern.predicate, p)

        store.update([Atom(p, Constant("x"), Constant("y"))])
        self.assertTrue(store.constants)
        self.assertTrue(store.terms)
        self.assertEqual(store.variables, set())

        store.remove_all([atom])
        self.assertNotIn(atom, store)
        self.assertGreaterEqual(len(store), 1)
        store.close()

    def test_remove_rejected_atom_is_noop(self):
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), AdHocSQLLayout())
        p = Predicate("p", 1)
        bad = Atom(p, Variable("X"))
        store.remove(bad)
        store.close()
