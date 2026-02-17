import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.rdbms.drivers import SQLiteDriver
from prototyping_inference_engine.api.data.storage.rdbms.layouts import (
    AdHocSQLLayout,
    EncodingAdHocSQLLayout,
    NaturalSQLLayout,
    TableSpec,
)
from prototyping_inference_engine.api.data.storage.rdbms_store import RDBMSStore


class TestRDBMSStore(unittest.TestCase):
    def test_adhoc_layout_insert_query_remove(self):
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), AdHocSQLLayout())
        p = Predicate("p", 2)
        atom = Atom(p, Constant("a"), Constant("b"))

        store.add(atom)

        query = BasicQuery(
            predicate=p,
            bound_positions={0: Constant("a")},
            answer_variables={1: Variable("Y")},
        )
        rows = list(store.evaluate(query))
        self.assertEqual(rows, [(Constant("b"),)])

        store.remove(atom)
        self.assertEqual(list(store.evaluate(query)), [])
        store.close()

    def test_encoding_layout_is_usable(self):
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), EncodingAdHocSQLLayout())
        p = Predicate("http://example.org/p", 1)
        atom = Atom(p, Constant("v"))
        store.add(atom)
        self.assertIn(atom, store)
        store.close()

    def test_natural_layout_rejects_unmapped_predicate(self):
        p = Predicate("mapped", 2)
        layout = NaturalSQLLayout({p: TableSpec("mapped_table", ("left", "right"))})
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), layout)

        with self.assertRaises(ValueError):
            store.add(Atom(Predicate("other", 2), Constant("a"), Constant("b")))

        store.close()
