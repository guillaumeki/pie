import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.data.schema import (
    IncompatiblePredicateSchemaError,
)
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)
from prototyping_inference_engine.api.data.storage.rdbms.drivers import SQLiteDriver
from prototyping_inference_engine.api.data.storage.rdbms.layouts import (
    NaturalSQLLayout,
    TableSpec,
)
from prototyping_inference_engine.api.data.storage.rdbms_store import RDBMSStore
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestReasoningSessionSchemaRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self) -> None:
        self.session.close()

    def test_evaluate_query_rejects_incompatible_predicate_schema(self):
        predicate = Predicate("p", 2)
        atom = Atom(predicate, Constant("a"), Constant("b"))
        query = FOQuery(atom, answer_variables=[])

        fact_base = InMemoryGraphStorage([atom])
        layout = NaturalSQLLayout({predicate: TableSpec("tab", ("left", "right"))})
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), layout)
        try:
            with self.assertRaises(IncompatiblePredicateSchemaError):
                list(
                    self.session.evaluate_query_with_sources(query, fact_base, [store])
                )
        finally:
            store.close()

    def test_create_knowledge_base_accepts_compatible_schema(self):
        predicate = Predicate("p", 1)
        fact_base_a = InMemoryGraphStorage([Atom(predicate, Constant("a"))])
        fact_base_b = InMemoryGraphStorage([Atom(predicate, Constant("b"))])

        kb_a = self.session.create_knowledge_base(fact_base=fact_base_a)
        kb_b = self.session.create_knowledge_base(fact_base=fact_base_b)

        self.assertIsNotNone(kb_a)
        self.assertIsNotNone(kb_b)

    def test_create_knowledge_base_rejects_incompatible_schema(self):
        predicate = Predicate("p", 1)
        fact_base = InMemoryGraphStorage([Atom(predicate, Constant("a"))])
        self.session.create_knowledge_base(fact_base=fact_base)

        layout = NaturalSQLLayout({predicate: TableSpec("tab", ("id",))})
        store = RDBMSStore(SQLiteDriver.from_path(":memory:"), layout)
        try:
            with self.assertRaises(IncompatiblePredicateSchemaError):
                self.session.create_knowledge_base(fact_base=store)
        finally:
            store.close()
