import unittest

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.rule_compilation.compilation_homomorphism import (
    CompilationAwareHomomorphismAlgorithm,
)
from prototyping_inference_engine.rule_compilation.no_compilation import NoCompilation


class TestCompilationAwareHomomorphism(unittest.TestCase):
    def setUp(self) -> None:
        self.p = Predicate("p", 1)
        self.q = Predicate("q", 1)
        self.x = Variable("X")
        self.a = Constant("a")

    def test_instance_is_cached(self) -> None:
        compilation = NoCompilation()
        algo1 = CompilationAwareHomomorphismAlgorithm.instance(compilation)
        algo2 = CompilationAwareHomomorphismAlgorithm.instance(compilation)
        self.assertIs(algo1, algo2)

    def test_computes_homomorphism_with_compatible_predicate(self) -> None:
        compilation = NoCompilation()
        algo = CompilationAwareHomomorphismAlgorithm.instance(compilation)
        from_atoms = FrozenAtomSet([Atom(self.p, self.x)])
        to_atoms = FrozenAtomSet([Atom(self.p, self.a)])
        results = list(algo.compute_homomorphisms(from_atoms, to_atoms))
        self.assertEqual(1, len(results))
        self.assertEqual(self.a, results[0][self.x])

    def test_incompatible_predicate_short_circuits(self) -> None:
        compilation = NoCompilation()
        algo = CompilationAwareHomomorphismAlgorithm.instance(compilation)
        from_atoms = FrozenAtomSet([Atom(self.p, self.x)])
        to_atoms = FrozenAtomSet([Atom(self.q, self.a)])
        results = list(algo.compute_homomorphisms(from_atoms, to_atoms))
        self.assertEqual([], results)


if __name__ == "__main__":
    unittest.main()
