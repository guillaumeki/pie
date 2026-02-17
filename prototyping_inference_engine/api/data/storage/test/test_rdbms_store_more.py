import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.rdbms.drivers import SQLiteDriver
from prototyping_inference_engine.api.data.storage.rdbms.layouts import (
    AdHocSQLLayout,
    NaturalSQLLayout,
    TableSpec,
)
from prototyping_inference_engine.api.data.storage.rdbms_store import RDBMSStore


class TestRDBMSStoreMore(unittest.TestCase):
    def test_iter_contains_and_terms(self):
        p = Predicate("p", 2)
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), AdHocSQLLayout())
        atom = Atom(p, Constant("a"), Constant("b"))
        store.add(atom)

        self.assertTrue(store.has_predicate(p))
        self.assertIn(p, set(store.get_predicates()))
        self.assertIn(atom, store)
        self.assertEqual(len(list(store)), 1)
        self.assertTrue(store.constants)
        self.assertTrue(store.terms)
        self.assertEqual(store.variables, set())
        store.close()

    def test_accepts_variable_atom_rejected(self):
        p = Predicate("p", 1)
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), AdHocSQLLayout())
        result = store.accepts_atom(Atom(p, Variable("X")))
        self.assertFalse(result.accepted)
        store.close()

    def test_unmapped_predicate_query_raises(self):
        p = Predicate("mapped", 1)
        other = Predicate("other", 1)
        layout = NaturalSQLLayout({p: TableSpec("mapped_tab", ("c0",))})
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), layout)
        with self.assertRaises(ValueError):
            list(
                store.evaluate(
                    BasicQuery(
                        other, bound_positions={}, answer_variables={0: Variable("X")}
                    )
                )
            )
        store.close()
