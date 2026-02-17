import unittest

from rdflib import BNode, Literal as RDFLiteral, URIRef
from rdflib.namespace import RDF

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.blank_node_term import BlankNodeTerm
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.atomic_pattern import UnconstrainedPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.storage.triple_store_storage import (
    TripleStoreStorage,
)


class TestTripleStoreStorageBranches(unittest.TestCase):
    def setUp(self):
        self.storage = TripleStoreStorage()

    def test_term_node_conversions(self):
        with self.assertRaises(ValueError):
            self.storage._term_to_node(Variable("X"))

        node = self.storage._term_to_node(BlankNodeTerm("b1"))
        self.assertIsInstance(node, BNode)

        literal = Literal(
            "42",
            "http://www.w3.org/2001/XMLSchema#integer",
            "42",
            None,
            ("http://www.w3.org/2001/XMLSchema#integer", "42", None),
        )
        lit_node = self.storage._term_to_node(literal)
        self.assertIsInstance(lit_node, RDFLiteral)

        self.assertIsInstance(self.storage._node_to_term(BNode("x")), BlankNodeTerm)
        self.assertIsInstance(
            self.storage._node_to_term(URIRef("http://e/s")), Constant
        )
        self.assertIsInstance(
            self.storage._node_to_term(
                RDFLiteral(
                    "42", datatype=URIRef("http://www.w3.org/2001/XMLSchema#integer")
                )
            ),
            Literal,
        )

    def test_atom_to_triple_paths_and_predicate_acceptance(self):
        unary = Atom(Predicate("http://e/C", 1), Constant("http://e/s"))
        binary = Atom(
            Predicate("http://e/p", 2),
            Constant("http://e/s"),
            Constant("http://e/o"),
        )
        self.storage._atom_to_triple(unary)
        self.storage._atom_to_triple(binary)
        with self.assertRaises(ValueError):
            self.storage._atom_to_triple(
                Atom(
                    Predicate("http://e/p3", 3),
                    Constant("a"),
                    Constant("b"),
                    Constant("c"),
                )
            )

        self.assertTrue(
            self.storage.accepts_predicate(Predicate("http://e/p", 2)).accepted
        )
        self.assertFalse(
            self.storage.accepts_predicate(Predicate("http://e/p", 4)).accepted
        )

    def test_accepts_atom_paths(self):
        ok = Atom(Predicate("http://e/p", 1), Constant("http://e/s"))
        bad_arity = Atom(
            Predicate("http://e/p", 3),
            Constant("a"),
            Constant("b"),
            Constant("c"),
        )
        bad_var = Atom(Predicate("http://e/p", 2), Variable("X"), Constant("x"))

        self.assertTrue(self.storage.accepts_atom(ok).accepted)
        self.assertFalse(self.storage.accepts_atom(bad_arity).accepted)
        self.assertFalse(self.storage.accepts_atom(bad_var).accepted)

    def test_get_predicates_has_predicate_and_iter(self):
        unary = Atom(Predicate("http://e/C", 1), Constant("http://e/s"))
        binary = Atom(
            Predicate("http://e/p", 2),
            Constant("http://e/s"),
            Constant("http://e/o"),
        )
        self.storage.update([unary, binary])

        predicates = set(self.storage.get_predicates())
        self.assertIn(Predicate("http://e/C", 1), predicates)
        self.assertIn(Predicate("http://e/p", 2), predicates)

        self.assertTrue(self.storage.has_predicate(Predicate("http://e/C", 1)))
        self.assertTrue(self.storage.has_predicate(Predicate("http://e/p", 2)))
        self.assertFalse(self.storage.has_predicate(Predicate("http://e/none", 3)))

        atoms = list(self.storage)
        self.assertEqual(len(atoms), 2)
        self.assertEqual(len(self.storage), 2)

        # Cover RDF.type with non-URI object branch
        self.storage._graph.add((URIRef("http://e/s3"), RDF.type, BNode("anon")))
        predicates = set(self.storage.get_predicates())
        self.assertIn(Predicate(str(RDF.type), 2), predicates)

    def test_evaluate_paths_and_patterns(self):
        p1 = Predicate("http://e/C", 1)
        p2 = Predicate("http://e/p", 2)
        self.storage.add(Atom(p1, Constant("http://e/s1")))
        self.storage.add(Atom(p2, Constant("http://e/s1"), Constant("http://e/o1")))

        pattern = self.storage.get_atomic_pattern(p2)
        self.assertIsInstance(pattern, UnconstrainedPattern)

        self.assertTrue(
            self.storage.can_evaluate(BasicQuery(p2, {}, {0: Variable("X")}))
        )
        self.assertFalse(
            self.storage.can_evaluate(
                BasicQuery(Predicate("x", 4), {}, {0: Variable("X")})
            )
        )

        unary_query = BasicQuery(p1, {}, {0: Variable("X")})
        self.assertEqual(len(list(self.storage.evaluate(unary_query))), 1)

        unary_bound = BasicQuery(
            p1,
            {0: Constant("http://e/s1")},
            {0: Variable("X")},
        )
        self.assertEqual(len(list(self.storage.evaluate(unary_bound))), 1)

        binary_query = BasicQuery(p2, {}, {0: Variable("X"), 1: Variable("Y")})
        self.assertEqual(len(list(self.storage.evaluate(binary_query))), 1)

        binary_bound = BasicQuery(
            p2,
            {0: Constant("http://e/s1"), 1: Constant("http://e/o1")},
            {},
        )
        self.assertEqual(list(self.storage.evaluate(binary_bound)), [tuple()])

        with self.assertRaises(ValueError):
            list(
                self.storage.evaluate(
                    BasicQuery(Predicate("x", 4), {}, {0: Variable("X")})
                )
            )

    def test_remove_remove_all_contains_and_term_views(self):
        p = Predicate("http://e/p", 2)
        atom = Atom(p, Constant("http://e/s"), Constant("http://e/o"))
        self.storage.add(atom)
        self.assertIn(atom, self.storage)

        bad_atom = Atom(
            Predicate("http://e/p", 2), Variable("X"), Constant("http://e/o")
        )
        self.assertNotIn(bad_atom, self.storage)

        self.assertEqual(self.storage.variables, set())
        self.assertTrue(self.storage.constants)
        self.assertTrue(self.storage.terms)

        self.storage.remove_all([atom])
        self.assertNotIn(atom, self.storage)

        # remove branch with rejected acceptance (variable term)
        self.storage.remove(bad_atom)

        # update branch
        self.storage.update([atom])
        self.assertIn(atom, self.storage)

        # direct RDF.type path for coverage in get_predicates / __iter__
        self.storage._graph.add(
            (URIRef("http://e/s2"), RDF.type, URIRef("http://e/C2"))
        )
        self.assertTrue(self.storage.has_predicate(Predicate("http://e/C2", 1)))
