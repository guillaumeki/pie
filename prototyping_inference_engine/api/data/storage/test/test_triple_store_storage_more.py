import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.blank_node_term import BlankNodeTerm
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.triple_store_storage import (
    TripleStoreStorage,
)


class TestTripleStoreStorageMore(unittest.TestCase):
    def test_unary_query_and_remove(self):
        storage = TripleStoreStorage()
        cls = Predicate("http://example.org/Class", 1)
        atom = Atom(cls, Constant("http://example.org/s"))
        storage.add(atom)

        q = BasicQuery(cls, bound_positions={}, answer_variables={0: Variable("X")})
        rows = list(storage.evaluate(q))
        self.assertEqual(rows, [(Constant("http://example.org/s"),)])

        storage.remove(atom)
        self.assertEqual(list(storage.evaluate(q)), [])

    def test_can_evaluate_false_for_arity_3(self):
        storage = TripleStoreStorage()
        q = BasicQuery(Predicate("http://example.org/p3", 3), {}, {0: Variable("X")})
        self.assertFalse(storage.can_evaluate(q))

    def test_terms_and_constants_collect(self):
        storage = TripleStoreStorage()
        p = Predicate("http://example.org/p", 2)
        atom = Atom(p, BlankNodeTerm("x"), Constant("http://example.org/o"))
        storage.add(atom)
        self.assertTrue(storage.terms)
        self.assertTrue(storage.constants)

    def test_literal_roundtrip(self):
        storage = TripleStoreStorage()
        p = Predicate("http://example.org/p", 2)
        lit = Literal(
            "42",
            "http://www.w3.org/2001/XMLSchema#integer",
            "42",
            None,
            ("http://www.w3.org/2001/XMLSchema#integer", "42", None),
        )
        atom = Atom(p, Constant("http://example.org/s"), lit)
        storage.add(atom)

        q = BasicQuery(
            p,
            bound_positions={0: Constant("http://example.org/s")},
            answer_variables={1: Variable("Y")},
        )
        rows = list(storage.evaluate(q))
        self.assertEqual(len(rows), 1)
        value = str(rows[0][0])
        self.assertIn("42", value)
