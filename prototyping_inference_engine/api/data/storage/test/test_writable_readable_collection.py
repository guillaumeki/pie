import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.data.collection.builder import (
    WritableReadableCollectionBuilder,
)
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)
from prototyping_inference_engine.api.data.storage.triple_store_storage import (
    TripleStoreStorage,
)


class TestWritableReadableCollection(unittest.TestCase):
    def test_heterogeneous_writing_routing(self):
        p = Predicate("p", 2)
        rdf_p = Predicate("http://example.org/likes", 2)

        memory = InMemoryGraphStorage()
        triple = TripleStoreStorage()

        collection = (
            WritableReadableCollectionBuilder()
            .add_predicate(p, memory)
            .set_default_writable(triple)
            .build()
        )

        atom_memory = Atom(p, Constant("a"), Constant("b"))
        atom_triple = Atom(
            rdf_p,
            Constant("http://example.org/a"),
            Constant("http://example.org/b"),
        )

        collection.add(atom_memory)
        collection.add(atom_triple)

        self.assertIn(atom_memory, memory)
        self.assertIn(atom_triple, triple)
