from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.fact_base import UnsupportedFactBaseOperation
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import FrozenInMemoryFactBase
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
from prototyping_inference_engine.api.query.atomic_query import AtomicQuery
from prototyping_inference_engine.api.query.unsupported_query import UnsupportedQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestFrozenInMemoryFactBase(TestCase):
    def test_instantiation_empty(self):
        """Test that FrozenInMemoryFactBase can be instantiated without arguments."""
        fb = FrozenInMemoryFactBase()
        self.assertEqual(len(fb.atom_set), 0)

    def test_instantiation_with_atoms(self):
        """Test that FrozenInMemoryFactBase can be instantiated with atoms."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), q(c).")
        fb = FrozenInMemoryFactBase(atoms)
        self.assertEqual(len(fb.atom_set), 2)

    def test_get_variables(self):
        """Test get_variables returns variables from the fact base."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(X,a).")
        fb = FrozenInMemoryFactBase(atoms)
        variables = fb.get_variables()
        self.assertEqual(variables, {Variable("X"), Variable("Y")})

    def test_get_constants(self):
        """Test get_constants returns constants from the fact base."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,a), q(b,c).")
        fb = FrozenInMemoryFactBase(atoms)
        constants = fb.get_constants()
        self.assertEqual(constants, {Constant("a"), Constant("b"), Constant("c")})

    def test_get_terms(self):
        """Test get_terms returns all terms from the fact base."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,a), q(Y).")
        fb = FrozenInMemoryFactBase(atoms)
        terms = fb.get_terms()
        self.assertEqual(terms, {Variable("X"), Variable("Y"), Constant("a")})

    def test_get_supported_operations(self):
        """Test that get_variables, get_constants, get_terms are supported operations."""
        supported = FrozenInMemoryFactBase.get_supported_operations()
        self.assertIn("get_variables", supported)
        self.assertIn("get_constants", supported)
        self.assertIn("get_terms", supported)

    def test_execute_atomic_query(self):
        """Test executing an atomic query."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(e).")
        fb = FrozenInMemoryFactBase(atoms)

        query_atom = Atom(Predicate("p", 2), Variable("X"), Variable("Y"))
        query = AtomicQuery(query_atom)

        results = list(fb.execute_query(query, Substitution()))
        self.assertEqual(len(results), 2)

        # Check that the results contain the expected tuples
        result_set = {tuple(r) for r in results}
        self.assertIn((Constant("a"), Constant("b")), result_set)
        self.assertIn((Constant("c"), Constant("d")), result_set)


class TestMutableInMemoryFactBase(TestCase):
    def test_instantiation_empty(self):
        """Test that MutableInMemoryFactBase can be instantiated without arguments."""
        fb = MutableInMemoryFactBase()
        self.assertEqual(len(fb.atom_set), 0)

    def test_instantiation_with_atoms(self):
        """Test that MutableInMemoryFactBase can be instantiated with atoms."""
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), q(c).")
        fb = MutableInMemoryFactBase(atoms)
        self.assertEqual(len(fb.atom_set), 2)

    def test_add_atom(self):
        """Test adding an atom to the fact base."""
        fb = MutableInMemoryFactBase()
        atom = Atom(Predicate("p", 2), Constant("a"), Constant("b"))
        fb.add(atom)
        self.assertEqual(len(fb.atom_set), 1)
        self.assertIn(atom, fb.atom_set)

    def test_update_atoms(self):
        """Test updating the fact base with multiple atoms."""
        fb = MutableInMemoryFactBase()
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), q(c), r(d,e,f).")
        fb.update(atoms)
        self.assertEqual(len(fb.atom_set), 3)

    def test_get_variables(self):
        """Test get_variables returns variables from the fact base."""
        fb = MutableInMemoryFactBase()
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,Y), q(X,a).")
        fb.update(atoms)
        variables = fb.get_variables()
        self.assertEqual(variables, {Variable("X"), Variable("Y")})

    def test_get_constants(self):
        """Test get_constants returns constants from the fact base."""
        fb = MutableInMemoryFactBase()
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,a), q(b,c).")
        fb.update(atoms)
        constants = fb.get_constants()
        self.assertEqual(constants, {Constant("a"), Constant("b"), Constant("c")})

    def test_get_terms(self):
        """Test get_terms returns all terms from the fact base."""
        fb = MutableInMemoryFactBase()
        atoms = Dlgp2Parser.instance().parse_atoms("p(X,a), q(Y).")
        fb.update(atoms)
        terms = fb.get_terms()
        self.assertEqual(terms, {Variable("X"), Variable("Y"), Constant("a")})

    def test_get_supported_operations(self):
        """Test that add, update, get_variables, get_constants, get_terms are supported."""
        supported = MutableInMemoryFactBase.get_supported_operations()
        self.assertIn("add", supported)
        self.assertIn("update", supported)
        self.assertIn("get_variables", supported)
        self.assertIn("get_constants", supported)
        self.assertIn("get_terms", supported)

    def test_execute_atomic_query(self):
        """Test executing an atomic query."""
        fb = MutableInMemoryFactBase()
        atoms = Dlgp2Parser.instance().parse_atoms("p(a,b), p(c,d), q(e).")
        fb.update(atoms)

        query_atom = Atom(Predicate("p", 2), Variable("X"), Variable("Y"))
        query = AtomicQuery(query_atom)

        results = list(fb.execute_query(query, Substitution()))
        self.assertEqual(len(results), 2)

    def test_add_after_instantiation(self):
        """Test adding atoms after instantiation with initial atoms."""
        initial_atoms = Dlgp2Parser.instance().parse_atoms("p(a,b).")
        fb = MutableInMemoryFactBase(initial_atoms)
        self.assertEqual(len(fb.atom_set), 1)

        new_atom = Atom(Predicate("q", 1), Constant("c"))
        fb.add(new_atom)
        self.assertEqual(len(fb.atom_set), 2)


class TestFactBaseOperations(TestCase):
    def test_get_all_operations(self):
        """Test that get_all_operations returns all defined operations."""
        all_ops = MutableInMemoryFactBase.get_all_operations()
        self.assertIn("add", all_ops)
        self.assertIn("update", all_ops)
        self.assertIn("get_variables", all_ops)
        self.assertIn("get_constants", all_ops)
        self.assertIn("get_terms", all_ops)

    def test_supported_query_types(self):
        """Test that supported query types are correctly reported."""
        self.assertEqual(FrozenInMemoryFactBase.get_supported_query_types(), (AtomicQuery,))
        self.assertEqual(MutableInMemoryFactBase.get_supported_query_types(), (AtomicQuery,))
