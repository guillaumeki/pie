import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.data.collection.builder import (
    WritableReadableCollectionBuilder,
)
from prototyping_inference_engine.api.data.collection.writable_readable_collection import (
    WritableReadableDataCollection,
)
from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.data.storage.builder import StorageBuilder
from prototyping_inference_engine.api.data.storage.rdbms.layouts import (
    NaturalSQLLayout,
    TableSpec,
)


class _ReadOnlySource(ReadableData):
    def __init__(self, predicate):
        self._predicate = predicate

    def get_predicates(self):
        return iter([self._predicate])

    def has_predicate(self, predicate):
        return predicate == self._predicate

    def get_atomic_pattern(self, predicate):
        raise KeyError

    def evaluate(self, query):
        return iter([])


class TestBuilderAndCollectionBranches(unittest.TestCase):
    def test_builder_branches(self):
        b = StorageBuilder.default_builder().use_in_memory_graph_store()
        self.assertIsNotNone(b.build())

        b = StorageBuilder.default_builder().use_in_memory_graph_store()
        self.assertIsNotNone(b.build())

        b = StorageBuilder.default_builder().use_triple_store()
        self.assertIsNotNone(b.build())

        b = (
            StorageBuilder.default_builder()
            .use_adhoc_sql_layout()
            .use_sqlite_db(":memory:")
        )
        s = b.build()
        s.close()

        # Driver selection branches
        b = StorageBuilder.default_builder().use_postgresql_db(
            "postgresql://user:pass@localhost:5432/db"
        )
        self.assertEqual(b._rdbms_driver.name, "postgresql")

        b = StorageBuilder.default_builder().use_mysql_db(
            host="localhost",
            port=3306,
            user="user",
            password="pass",
            database="db",
        )
        self.assertEqual(b._rdbms_driver.name, "mysql")

        b = StorageBuilder.default_builder().use_hsqldb("jdbc:hsqldb:mem:mymemdb")
        self.assertEqual(b._rdbms_driver.name, "hsqldb")

    def test_builder_rdbms_default_path(self):
        b = StorageBuilder.default_builder()
        b._kind = b._kind.RDBMS
        s = b.build()
        s.close()

        b = (
            StorageBuilder.default_builder()
            .use_encoding_adhoc_sql_layout()
            .use_sqlite_db(":memory:")
        )
        s = b.build()
        s.close()

        p = Predicate("mapped", 1)
        layout = NaturalSQLLayout({p: TableSpec("mapped", ("c0",))})
        b = (
            StorageBuilder.default_builder()
            .use_natural_sql_layout(layout)
            .use_sqlite_db(":memory:")
        )
        s = b.build()
        s.close()

    def test_writable_readable_default_fallback(self):
        p = Predicate("p", 1)
        q = Predicate("q", 1)
        ro = _ReadOnlySource(p)
        w = StorageBuilder.default_builder().use_in_memory_graph_store().build()
        coll = WritableReadableDataCollection({p: ro}, default_writable=w)

        atom_q = Atom(q, Constant("a"))
        coll.add(atom_q)
        self.assertTrue(w.has_predicate(q))

    def test_writable_readable_builder_dynamic(self):
        p = Predicate("p", 1)
        source = StorageBuilder.default_builder().use_in_memory_graph_store().build()
        coll = (
            WritableReadableCollectionBuilder()
            .add_predicate(p, source)
            .add_dynamic_source(source)
            .set_default_writable(source)
            .build()
        )
        coll.add(Atom(p, Constant("x")))
        self.assertTrue(source.has_predicate(p))

    def test_writable_readable_remove_key_error(self):
        p = Predicate("p", 1)
        ro = _ReadOnlySource(p)
        coll = WritableReadableDataCollection({p: ro})
        with self.assertRaises(KeyError):
            coll.remove(Atom(Predicate("q", 1), Constant("a")))
