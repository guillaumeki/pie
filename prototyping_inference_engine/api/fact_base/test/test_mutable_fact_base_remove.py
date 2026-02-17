"""Tests for remove operations on MutableInMemoryFactBase."""

import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)


class TestMutableInMemoryFactBaseRemove(unittest.TestCase):
    def test_remove(self) -> None:
        atom = Atom(Predicate("p", 1), Constant("a"))
        fb = MutableInMemoryFactBase([atom])
        fb.remove(atom)
        self.assertNotIn(atom, fb)

    def test_remove_all(self) -> None:
        p = Predicate("p", 1)
        atoms = (Atom(p, Constant("a")), Atom(p, Constant("b")))
        fb = MutableInMemoryFactBase(atoms)
        fb.remove_all(atoms)
        self.assertEqual(len(fb), 0)


if __name__ == "__main__":
    unittest.main()
