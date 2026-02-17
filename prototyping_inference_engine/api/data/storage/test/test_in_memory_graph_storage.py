import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)


class _GraphStorageContractTests:
    def _make_storage(self, atoms):
        return InMemoryGraphStorage(atoms)

    def _build_storage(self):
        p = Predicate("p", 2)
        q = Predicate("q", 1)
        atoms = [
            Atom(p, Constant("a"), Constant("b")),
            Atom(p, Constant("a"), Constant("c")),
            Atom(q, Constant("a")),
        ]
        return self._make_storage(atoms), p, q

    def test_basic_read_write(self):
        storage, p, _ = self._build_storage()
        self.assertEqual(len(storage), 3)
        self.assertTrue(storage.has_predicate(p))

        atom = Atom(p, Constant("x"), Constant("y"))
        storage.add(atom)
        self.assertIn(atom, storage)

        storage.remove(atom)
        self.assertNotIn(atom, storage)

    def test_evaluate(self):
        storage, p, _ = self._build_storage()
        query = BasicQuery(
            predicate=p,
            bound_positions={0: Constant("a")},
            answer_variables={1: Variable("Y")},
        )
        rows = {tuple(row) for row in storage.evaluate(query)}
        self.assertEqual(rows, {(Constant("b"),), (Constant("c"),)})


class TestInMemoryGraphStorage(_GraphStorageContractTests, unittest.TestCase):
    def _make_storage(self, atoms):
        return InMemoryGraphStorage(atoms)
