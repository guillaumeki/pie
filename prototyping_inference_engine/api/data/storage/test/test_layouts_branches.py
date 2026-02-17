import sqlite3
import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.rdbms.layouts import (
    AdHocSQLLayout,
    EncodingAdHocSQLLayout,
    LogicalType,
    NaturalSQLLayout,
    TableSpec,
    _safe_name,
)


class TestLayoutsBranches(unittest.TestCase):
    def test_safe_name_and_not_implemented_base(self):
        self.assertEqual(_safe_name("http://e/p-1"), "http___e_p_1")
        layout = AdHocSQLLayout()
        with self.assertRaises(NotImplementedError):
            layout._table_name = lambda predicate: (_ for _ in ()).throw(
                NotImplementedError()
            )  # type: ignore[method-assign]
            layout._table_name(Predicate("p", 1))

    def test_dynamic_layout_select_without_where(self):
        p = Predicate("p", 1)
        for layout in (AdHocSQLLayout(), EncodingAdHocSQLLayout()):
            conn = sqlite3.connect(":memory:")
            cur = conn.cursor()
            layout.ensure_schema(cur, p)
            sql, params = layout.insert_sql(Atom(p, Constant("a")))
            cur.execute(sql, params)
            conn.commit()

            plan = layout.select_sql(BasicQuery(p, {}, {0: Variable("X")}))
            cur.execute(plan.sql, plan.params)
            rows = cur.fetchall()
            self.assertEqual(rows, [("a",)])
            conn.close()

    def test_natural_layout_rejections(self):
        p_bad = Predicate("p", 2)
        natural = NaturalSQLLayout({p_bad: TableSpec("tab", ("c0",))})
        rejected = natural.accepts_predicate(p_bad)
        self.assertFalse(rejected.accepted)

        with self.assertRaises(ValueError):
            natural.ensure_schema(
                sqlite3.connect(":memory:").cursor(), Predicate("other", 1)
            )

        with self.assertRaises(ValueError):
            natural.insert_sql(Atom(Predicate("other", 1), Constant("a")))

    def test_natural_layout_non_sqlite_discovery(self):
        class FakeCursor:
            def __init__(self):
                self._rows = [
                    ("people", "id", "integer", "NO"),
                    ("people", "name", "varchar", "YES"),
                    ("flags", "ok", "boolean", "NO"),
                ]

            def execute(self, _sql):
                return None

            def fetchall(self):
                return list(self._rows)

        class FakeConnection:
            def cursor(self):
                return FakeCursor()

        layout = NaturalSQLLayout(auto_discover=True)
        layout.bind(FakeConnection(), "postgresql")

        discovered = set(layout.known_predicates())
        self.assertIn(Predicate("people", 2), discovered)
        self.assertIn(Predicate("flags", 1), discovered)

        people_schema = layout.get_schema(Predicate("people", 2))
        self.assertIsNotNone(people_schema)
        if people_schema is None:
            self.fail("Expected discovered schema for people")
        self.assertEqual(people_schema.positions[0].logical_type, LogicalType.INTEGER)
        self.assertEqual(people_schema.positions[1].logical_type, LogicalType.STRING)
        self.assertTrue(people_schema.positions[1].nullable)

    def test_natural_layout_discovery_exception_is_best_effort(self):
        class FailingCursor:
            def execute(self, _sql):
                raise RuntimeError("boom")

            def fetchall(self):
                return []

        class FailingConnection:
            def cursor(self):
                return FailingCursor()

        predicate = Predicate("missing", 1)
        layout = NaturalSQLLayout(auto_discover=True)
        layout.bind(FailingConnection(), "sqlite")

        self.assertEqual(tuple(layout.known_predicates()), tuple())
        self.assertIsNone(layout.get_schema(predicate))
