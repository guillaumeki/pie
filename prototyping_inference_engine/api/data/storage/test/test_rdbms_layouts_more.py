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
)


class TestRDBMSLayoutsMore(unittest.TestCase):
    def test_adhoc_and_encoding_known_predicates(self):
        p = Predicate("p", 2)
        atom = Atom(p, Constant("a"), Constant("b"))

        for layout in (AdHocSQLLayout(), EncodingAdHocSQLLayout()):
            conn = sqlite3.connect(":memory:")
            cur = conn.cursor()
            layout.ensure_schema(cur, p)
            sql, params = layout.insert_sql(atom)
            cur.execute(sql, params)
            conn.commit()
            self.assertIn(p, set(layout.known_predicates()))
            conn.close()

    def test_natural_positive_paths(self):
        p = Predicate("p", 2)
        layout = NaturalSQLLayout({p: TableSpec("tab", ("left", "right"))})
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE tab (left TEXT NOT NULL, right TEXT NOT NULL, PRIMARY KEY (left, right))"
        )

        self.assertTrue(layout.accepts_predicate(p).accepted)
        layout.ensure_schema(cur, p)

        atom = Atom(p, Constant("a"), Constant("b"))
        sql, params = layout.insert_sql(atom)
        cur.execute(sql, params)
        conn.commit()

        query = BasicQuery(
            predicate=p,
            bound_positions={0: Constant("a")},
            answer_variables={1: Variable("Y")},
        )
        plan = layout.select_sql(query)
        cur.execute(plan.sql, plan.params)
        rows = cur.fetchall()
        self.assertEqual(rows, [("b",)])
        conn.close()

    def test_natural_layout_auto_discovery_sqlite(self):
        conn = sqlite3.connect(":memory:")
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE employee (id INTEGER NOT NULL, name TEXT, PRIMARY KEY (id))"
        )
        conn.commit()

        layout = NaturalSQLLayout(auto_discover=True)
        layout.bind(conn, "sqlite")

        predicate = Predicate("employee", 2)
        self.assertTrue(layout.accepts_predicate(predicate).accepted)
        schema = layout.get_schema(predicate)
        self.assertIsNotNone(schema)
        if schema is None:
            self.fail("Expected auto-discovered schema for employee")

        self.assertEqual(schema.positions[0].name, "id")
        self.assertEqual(schema.positions[0].logical_type, LogicalType.INTEGER)
        self.assertFalse(schema.positions[0].nullable)
        self.assertEqual(schema.positions[1].name, "name")
        self.assertEqual(schema.positions[1].logical_type, LogicalType.STRING)
        self.assertTrue(schema.positions[1].nullable)
        conn.close()
