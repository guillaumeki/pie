import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.blank_node_term import BlankNodeTerm
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.triple_store_storage import (
    TripleStoreStorage,
)


class TestTripleStoreStorage(unittest.TestCase):
    def test_binary_and_unary_roundtrip(self):
        storage = TripleStoreStorage()
        p = Predicate("http://example.org/p", 2)
        cls = Predicate("http://example.org/Class", 1)

        atom_binary = Atom(
            p,
            Constant("http://example.org/alice"),
            Constant("http://example.org/bob"),
        )
        atom_unary = Atom(cls, Constant("http://example.org/alice"))

        storage.add(atom_binary)
        storage.add(atom_unary)

        self.assertIn(atom_binary, storage)
        self.assertIn(atom_unary, storage)
        self.assertTrue(storage.has_predicate(p))
        self.assertTrue(storage.has_predicate(cls))

    def test_query_binary(self):
        storage = TripleStoreStorage()
        p = Predicate("http://example.org/p", 2)
        storage.add(
            Atom(
                p,
                Constant("http://example.org/a"),
                Constant("http://example.org/b"),
            )
        )

        query = BasicQuery(
            predicate=p,
            bound_positions={0: Constant("http://example.org/a")},
            answer_variables={1: Variable("Y")},
        )
        rows = list(storage.evaluate(query))
        self.assertEqual(rows, [(Constant("http://example.org/b"),)])

    def test_reject_arity_over_two(self):
        storage = TripleStoreStorage()
        predicate = Predicate("http://example.org/p3", 3)
        atom = Atom(
            predicate,
            Constant("http://example.org/a"),
            Constant("http://example.org/b"),
            Constant("http://example.org/c"),
        )
        with self.assertRaises(ValueError):
            storage.add(atom)

    def test_reject_variable_in_atom(self):
        storage = TripleStoreStorage()
        p = Predicate("http://example.org/p", 2)
        atom = Atom(p, Variable("X"), Constant("http://example.org/b"))
        with self.assertRaises(ValueError):
            storage.add(atom)

    def test_blank_node_roundtrip(self):
        storage = TripleStoreStorage()
        p = Predicate("http://example.org/p", 2)
        atom = Atom(p, BlankNodeTerm("b0"), Constant("http://example.org/o"))
        storage.add(atom)
        materialized = list(storage)
        self.assertEqual(len(materialized), 1)
        result = materialized[0]
        self.assertIsInstance(result.terms[0], BlankNodeTerm)
        self.assertFalse(result.terms[0].is_ground)
