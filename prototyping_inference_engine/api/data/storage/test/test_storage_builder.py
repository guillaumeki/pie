import unittest

from prototyping_inference_engine.api.data.storage.builder import StorageBuilder
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)
from prototyping_inference_engine.api.data.storage.rdbms_store import RDBMSStore
from prototyping_inference_engine.api.data.storage.triple_store_storage import (
    TripleStoreStorage,
)


class TestStorageBuilder(unittest.TestCase):
    def test_default_storage(self):
        storage = StorageBuilder.default_storage()
        self.assertIsInstance(storage, InMemoryGraphStorage)

    def test_in_memory_graph(self):
        storage = StorageBuilder.default_builder().use_in_memory_graph_store().build()
        self.assertIsInstance(storage, InMemoryGraphStorage)

    def test_triple_store(self):
        storage = StorageBuilder.default_builder().use_triple_store().build()
        self.assertIsInstance(storage, TripleStoreStorage)

    def test_rdbms(self):
        storage = StorageBuilder.default_builder().use_sqlite_db(":memory:").build()
        self.assertIsInstance(storage, RDBMSStore)
        storage.close()
