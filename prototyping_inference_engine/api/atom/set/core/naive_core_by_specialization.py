from functools import cache
from typing import TypeVar

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import HomomorphismAlgorithm
from prototyping_inference_engine.api.atom.set.homomorphism.naive_backtrack_homomorphism_algorithm import NaiveBacktrackHomomorphismAlgorithm
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution

AS = TypeVar("AS", bound=AtomSet)


class NaiveCoreBySpecialization(CoreAlgorithm):
    def __init__(self, homomorphism_algorithm: HomomorphismAlgorithm = None):
        if homomorphism_algorithm:
            self._homomorphism_algorithm: HomomorphismAlgorithm = homomorphism_algorithm
        else:
            self._homomorphism_algorithm: HomomorphismAlgorithm = NaiveBacktrackHomomorphismAlgorithm.instance()

    @staticmethod
    @cache
    def instance() -> "NaiveCoreBySpecialization":
        return NaiveCoreBySpecialization()

    def compute_core(self, atom_set: AS, freeze: tuple[Variable] = None) -> AS:
        if freeze is None:
            freeze = tuple()
        new_atom_set = atom_set
        pre_sub = Substitution({v: v for v in freeze})
        for h in self._homomorphism_algorithm.compute_homomorphisms(atom_set, atom_set, pre_sub):
            specialization = h(atom_set)
            if len(specialization) < len(new_atom_set):
                new_atom_set = specialization
        return new_atom_set
