import unittest

try:
    from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - optional dependency
    PostgresContainer = None

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.rdbms.drivers import PostgreSQLDriver
from prototyping_inference_engine.api.data.storage.rdbms.layouts import AdHocSQLLayout
from prototyping_inference_engine.api.data.storage.rdbms_store import RDBMSStore


@unittest.skipUnless(PostgresContainer is not None, "testcontainers not available")
class TestPostgresRDBMSStoreIntegration(unittest.TestCase):
    def test_roundtrip_with_postgres_container(self):
        try:
            container = PostgresContainer("postgres:16-alpine")
            container.start()
        except Exception as exc:  # pragma: no cover - runtime environment dependent
            self.skipTest(f"Docker/Postgres container unavailable: {exc}")
            return

        try:
            dsn = container.get_connection_url()
            store = RDBMSStore(PostgreSQLDriver.from_dsn(dsn), AdHocSQLLayout())
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
            store.close()
        finally:
            container.stop()
