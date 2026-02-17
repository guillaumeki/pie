import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)
from prototyping_inference_engine.api.data.storage.virtual_delete_storage import (
    VirtualDeleteStorage,
)


class TestVirtualDeleteStorage(unittest.TestCase):
    def test_virtual_delete_and_concrete(self):
        p = Predicate("p", 1)
        atom = Atom(p, Constant("a"))
        base = InMemoryGraphStorage([atom])
        wrapper = VirtualDeleteStorage(base)

        wrapper.remove(atom)
        self.assertNotIn(atom, wrapper)
        self.assertIn(atom, base)

        wrapper.concrete_deletions()
        self.assertNotIn(atom, base)
