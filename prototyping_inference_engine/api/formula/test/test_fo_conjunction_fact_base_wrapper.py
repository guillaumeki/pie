"""
Tests for FOConjunctionFactBaseWrapper.
"""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.formula import ConjunctionFormula
from prototyping_inference_engine.api.formula.fo_conjunction_fact_base_wrapper import (
    FOConjunctionFactBaseWrapper,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution


class TestFOConjunctionFactBaseWrapper(unittest.TestCase):
    def setUp(self):
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.y = Variable("Y")
        self.a = Constant("a")

    def test_atoms_and_variables(self):
        atom1 = Atom(self.p, self.x)
        atom2 = Atom(self.q, self.y)
        fact_base = FrozenInMemoryFactBase([atom1, atom2])
        wrapper = FOConjunctionFactBaseWrapper(fact_base)
        self.assertEqual(wrapper.atoms, frozenset([atom1, atom2]))
        self.assertEqual(wrapper.free_variables, frozenset([self.x, self.y]))
        self.assertEqual(wrapper.bound_variables, frozenset())

    def test_apply_substitution(self):
        atom1 = Atom(self.p, self.x)
        atom2 = Atom(self.q, self.y)
        fact_base = FrozenInMemoryFactBase([atom1, atom2])
        wrapper = FOConjunctionFactBaseWrapper(fact_base)
        sub = Substitution({self.x: self.a})
        result = wrapper.apply_substitution(sub)
        self.assertIsInstance(result, ConjunctionFormula)
        expected = ConjunctionFormula(Atom(self.p, self.a), Atom(self.q, self.y))
        self.assertEqual(result, expected)

    def test_empty_fact_base(self):
        fact_base = FrozenInMemoryFactBase()
        wrapper = FOConjunctionFactBaseWrapper(fact_base)
        sub = Substitution({self.x: self.a})
        result = wrapper.apply_substitution(sub)
        self.assertIs(result, wrapper)
