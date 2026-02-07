from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.factory import FactBaseFactory
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.api.fact_base.protocols import (
    TermInspectable,
    Writable,
    Enumerable,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestFrozenInMemoryFactBase(TestCase):
    def test_instantiation_empty(self):
        """Test that FrozenInMemoryFactBase can be instantiated without arguments."""
        fb = FrozenInMemoryFactBase()
        self.assertEqual(len(fb), 0)

    def test_instantiation_with_atoms(self):
        """Test that FrozenInMemoryFactBase can be instantiated with atoms."""
        atoms = DlgpeParser.instance().parse_atoms("p(a,b), q(c).")
        fb = FrozenInMemoryFactBase(atoms)
        self.assertEqual(len(fb), 2)

    def test_variables(self):
        """Test variables property returns variables from the fact base."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(X,a).")
        fb = FrozenInMemoryFactBase(atoms)
        self.assertEqual(fb.variables, {Variable("X"), Variable("Y")})

    def test_constants(self):
        """Test constants property returns constants from the fact base."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,a), q(b,c).")
        fb = FrozenInMemoryFactBase(atoms)
        self.assertEqual(fb.constants, {Constant("a"), Constant("b"), Constant("c")})

    def test_terms(self):
        """Test terms property returns all terms from the fact base."""
        atoms = DlgpeParser.instance().parse_atoms("p(X,a), q(Y).")
        fb = FrozenInMemoryFactBase(atoms)
        self.assertEqual(fb.terms, {Variable("X"), Variable("Y"), Constant("a")})


class TestMutableInMemoryFactBase(TestCase):
    def test_instantiation_empty(self):
        """Test that MutableInMemoryFactBase can be instantiated without arguments."""
        fb = MutableInMemoryFactBase()
        self.assertEqual(len(fb), 0)

    def test_instantiation_with_atoms(self):
        """Test that MutableInMemoryFactBase can be instantiated with atoms."""
        atoms = DlgpeParser.instance().parse_atoms("p(a,b), q(c).")
        fb = MutableInMemoryFactBase(atoms)
        self.assertEqual(len(fb), 2)

    def test_add_atom(self):
        """Test adding an atom to the fact base."""
        fb = MutableInMemoryFactBase()
        atom = Atom(Predicate("p", 2), Constant("a"), Constant("b"))
        fb.add(atom)
        self.assertEqual(len(fb), 1)
        self.assertIn(atom, fb)

    def test_update_atoms(self):
        """Test updating the fact base with multiple atoms."""
        fb = MutableInMemoryFactBase()
        atoms = DlgpeParser.instance().parse_atoms("p(a,b), q(c), r(d,e,f).")
        fb.update(atoms)
        self.assertEqual(len(fb), 3)

    def test_variables(self):
        """Test variables property returns variables from the fact base."""
        fb = MutableInMemoryFactBase()
        atoms = DlgpeParser.instance().parse_atoms("p(X,Y), q(X,a).")
        fb.update(atoms)
        self.assertEqual(fb.variables, {Variable("X"), Variable("Y")})

    def test_constants(self):
        """Test constants property returns constants from the fact base."""
        fb = MutableInMemoryFactBase()
        atoms = DlgpeParser.instance().parse_atoms("p(X,a), q(b,c).")
        fb.update(atoms)
        self.assertEqual(fb.constants, {Constant("a"), Constant("b"), Constant("c")})

    def test_terms(self):
        """Test terms property returns all terms from the fact base."""
        fb = MutableInMemoryFactBase()
        atoms = DlgpeParser.instance().parse_atoms("p(X,a), q(Y).")
        fb.update(atoms)
        self.assertEqual(fb.terms, {Variable("X"), Variable("Y"), Constant("a")})

    def test_add_after_instantiation(self):
        """Test adding atoms after instantiation with initial atoms."""
        initial_atoms = DlgpeParser.instance().parse_atoms("p(a,b).")
        fb = MutableInMemoryFactBase(initial_atoms)
        self.assertEqual(len(fb), 1)

        new_atom = Atom(Predicate("q", 1), Constant("c"))
        fb.add(new_atom)
        self.assertEqual(len(fb), 2)


class TestProtocols(TestCase):
    def test_frozen_is_term_inspectable(self):
        """Test that FrozenInMemoryFactBase implements TermInspectable."""
        fb = FrozenInMemoryFactBase()
        self.assertIsInstance(fb, TermInspectable)

    def test_mutable_is_term_inspectable(self):
        """Test that MutableInMemoryFactBase implements TermInspectable."""
        fb = MutableInMemoryFactBase()
        self.assertIsInstance(fb, TermInspectable)

    def test_mutable_is_writable(self):
        """Test that MutableInMemoryFactBase implements Writable."""
        fb = MutableInMemoryFactBase()
        self.assertIsInstance(fb, Writable)

    def test_frozen_is_not_writable(self):
        """Test that FrozenInMemoryFactBase does not implement Writable."""
        fb = FrozenInMemoryFactBase()
        self.assertNotIsInstance(fb, Writable)

    def test_frozen_is_enumerable(self):
        """Test that FrozenInMemoryFactBase implements Enumerable."""
        fb = FrozenInMemoryFactBase()
        self.assertIsInstance(fb, Enumerable)

    def test_mutable_is_enumerable(self):
        """Test that MutableInMemoryFactBase implements Enumerable."""
        fb = MutableInMemoryFactBase()
        self.assertIsInstance(fb, Enumerable)


class TestEnumerable(TestCase):
    def test_len(self):
        """Test len() on fact base."""
        atoms = DlgpeParser.instance().parse_atoms("p(a), q(b).")
        fb = FrozenInMemoryFactBase(atoms)
        self.assertEqual(len(fb), 2)

    def test_iter(self):
        """Test iteration over fact base."""
        atoms = DlgpeParser.instance().parse_atoms("p(a), q(b).")
        fb = FrozenInMemoryFactBase(atoms)
        self.assertEqual(len(list(fb)), 2)

    def test_contains(self):
        """Test 'in' operator on fact base."""
        atom = Atom(Predicate("p", 1), Constant("a"))
        fb = FrozenInMemoryFactBase([atom])
        self.assertIn(atom, fb)

    def test_not_contains(self):
        """Test 'in' operator returns False for missing atom."""
        atom1 = Atom(Predicate("p", 1), Constant("a"))
        atom2 = Atom(Predicate("q", 1), Constant("b"))
        fb = FrozenInMemoryFactBase([atom1])
        self.assertNotIn(atom2, fb)


class TestFactory(TestCase):
    def test_create_frozen(self):
        """Test factory creates FrozenInMemoryFactBase."""
        fb = FactBaseFactory.create_frozen()
        self.assertIsInstance(fb, FrozenInMemoryFactBase)

    def test_create_frozen_with_atoms(self):
        """Test factory creates FrozenInMemoryFactBase with atoms."""
        atoms = DlgpeParser.instance().parse_atoms("p(a), q(b).")
        fb = FactBaseFactory.create_frozen(atoms)
        self.assertIsInstance(fb, FrozenInMemoryFactBase)
        self.assertEqual(len(fb), 2)

    def test_create_mutable(self):
        """Test factory creates MutableInMemoryFactBase."""
        fb = FactBaseFactory.create_mutable()
        self.assertIsInstance(fb, MutableInMemoryFactBase)

    def test_create_mutable_with_atoms(self):
        """Test factory creates MutableInMemoryFactBase with atoms."""
        atoms = DlgpeParser.instance().parse_atoms("p(a), q(b).")
        fb = FactBaseFactory.create_mutable(atoms)
        self.assertIsInstance(fb, MutableInMemoryFactBase)
        self.assertEqual(len(fb), 2)
