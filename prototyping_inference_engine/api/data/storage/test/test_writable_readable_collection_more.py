import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.data.collection.writable_readable_collection import (
    WritableReadableDataCollection,
)
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)


class TestWritableReadableCollectionMore(unittest.TestCase):
    def test_remove_and_update(self):
        p = Predicate("p", 1)
        source = InMemoryGraphStorage()
        coll = WritableReadableDataCollection({p: source})
        a = Atom(p, Constant("a"))
        b = Atom(p, Constant("b"))
        coll.update([a, b])
        self.assertIn(a, source)
        coll.remove(a)
        self.assertNotIn(a, source)
        coll.remove_all([b])
        self.assertNotIn(b, source)

    def test_key_error_without_writable(self):
        p = Predicate("p", 1)
        q = Predicate("q", 1)
        source = InMemoryGraphStorage()
        coll = WritableReadableDataCollection({p: source}, default_writable=None)
        with self.assertRaises(KeyError):
            coll.add(Atom(q, Constant("x")))
