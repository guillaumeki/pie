import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.in_memory_graph_storage import (
    InMemoryGraphStorage,
)


class TestInMemoryGraphStorageMore(unittest.TestCase):
    def test_remove_non_existing_and_predicates(self):
        p = Predicate("p", 2)
        s = InMemoryGraphStorage()
        atom = Atom(p, Constant("a"), Constant("b"))
        s.remove(atom)
        self.assertFalse(s.has_predicate(p))
        self.assertEqual(list(s.get_predicates()), [])

    def test_query_no_answers(self):
        p = Predicate("p", 2)
        s = InMemoryGraphStorage([Atom(p, Constant("a"), Constant("b"))])
        q = BasicQuery(
            predicate=p,
            bound_positions={0: Constant("a"), 1: Constant("b")},
            answer_variables={},
        )
        self.assertEqual(list(s.evaluate(q)), [tuple()])

    def test_variables_constants_terms(self):
        p = Predicate("p", 2)
        s = InMemoryGraphStorage([Atom(p, Variable("X"), Constant("a"))])
        self.assertTrue(s.variables)
        self.assertTrue(s.constants)
        self.assertTrue(s.terms)

    def test_schema_pattern_membership_and_bulk_remove(self):
        predicate = Predicate("edge", 2)
        atom_a = Atom(predicate, Constant("a"), Constant("b"))
        atom_b = Atom(predicate, Constant("b"), Constant("c"))
        storage = InMemoryGraphStorage([atom_a, atom_b])

        pattern = storage.get_atomic_pattern(predicate)
        self.assertEqual(pattern.predicate, predicate)
        self.assertIn(atom_a, storage)
        self.assertEqual(len(storage), 2)

        schema = storage.get_schema(predicate)
        self.assertIsNotNone(schema)
        missing = storage.get_schema(Predicate("missing", 1))
        self.assertIsNone(missing)
        schemas = tuple(storage.get_schemas())
        self.assertEqual(len(schemas), 1)
        self.assertEqual(schemas[0].predicate, predicate)

        q = BasicQuery(
            predicate=predicate,
            bound_positions={0: Constant("z")},
            answer_variables={1: Variable("Y")},
        )
        self.assertEqual(list(storage.evaluate(q)), [])

        storage.remove_all([atom_a, atom_b])
        self.assertEqual(len(storage), 0)
        self.assertFalse(storage.has_predicate(predicate))
