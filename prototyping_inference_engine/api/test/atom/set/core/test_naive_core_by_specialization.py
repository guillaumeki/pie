from unittest import TestCase

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.core.naive_core_by_specialization import NaiveCoreBySpecialization
from prototyping_inference_engine.api.atom.set.homomorphism.naive_backtrack_homomorphism_algorithm import NaiveBacktrackHomomorphismAlgorithm
from src.prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestNaiveCoreBySpecialization(TestCase):
    data = ({"atom_set": "p(X), t(X,a,b), s(a,z), p(Y), t(Y,a,b), relatedTo(Y,z)."},
            {"atom_set": "p(a,X), p(X,Z), p(X,Y), p(Y,Z)."},
            {"atom_set": "p(a,X), p(X,Z), p(X,Y), p(Y,Z), p(a,a)."},
            {"atom_set": "p(Z0,V0), q(a, Z0), q(Z0,a), q(Z0,c), q(c,Z0), p(a,b), p(c,d), p(Z1,V1), q(a, Z1), q(Z1,"
                         "a), q(Z1,c), q(c,Z1)."})

    @staticmethod
    def _is_a_core(atom_set: AtomSet) -> bool:
        for h in NaiveBacktrackHomomorphismAlgorithm.instance().compute_homomorphisms(atom_set, atom_set):
            if len(h(atom_set)) < len(atom_set):
                return False
        return True

    @staticmethod
    def _is_equivalent(as1: AtomSet, as2: AtomSet) -> bool:
        return (NaiveBacktrackHomomorphismAlgorithm.instance().exist_homomorphism(as1, as2)
                and NaiveBacktrackHomomorphismAlgorithm.instance().exist_homomorphism(as2, as1))

    def test_compute_core(self):
        for d in self.data:
            atom_set = Dlgp2Parser.instance().parse_atoms(d["atom_set"])
            core = NaiveCoreBySpecialization.instance().compute_core(atom_set)

            # print(core)
            # print(atom_set)

            self.assertTrue(self._is_a_core(core))
            self.assertTrue(self._is_equivalent(core, atom_set))
