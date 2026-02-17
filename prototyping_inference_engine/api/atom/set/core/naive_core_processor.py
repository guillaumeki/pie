"""Naive core processor implementation."""

from __future__ import annotations

from functools import cache
from typing import Optional, TypeVar

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.atom.set.core.core_algorithm import CoreAlgorithm
from prototyping_inference_engine.api.atom.set.core.core_helpers import (
    atoms_with_variable,
    freeze_substitution,
    to_same_type,
    without_atoms,
)
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import (
    HomomorphismAlgorithm,
)
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm_provider import (
    DefaultHomomorphismAlgorithmProvider,
    HomomorphismAlgorithmProvider,
)
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.atom.term.variable import Variable

AS = TypeVar("AS", bound=AtomSet)


class NaiveCoreProcessor(CoreAlgorithm):
    """Naive core computation by variable deletion tests."""

    def __init__(
        self, algorithm_provider: Optional[HomomorphismAlgorithmProvider] = None
    ) -> None:
        if algorithm_provider is None:
            algorithm_provider = DefaultHomomorphismAlgorithmProvider()
        self._homomorphism_algorithm: HomomorphismAlgorithm = (
            algorithm_provider.get_algorithm()
        )

    @staticmethod
    @cache
    def instance() -> "NaiveCoreProcessor":
        return NaiveCoreProcessor()

    def compute_core(
        self, atom_set: AS, freeze: Optional[tuple[Variable, ...]] = None
    ) -> AS:
        freeze = tuple() if freeze is None else freeze
        frozen_set = set(freeze)
        pre_sub = freeze_substitution(freeze)

        target = MutableAtomSet(atom_set)
        variables = [v for v in target.variables if v not in frozen_set]

        for var in variables:
            atoms_using_var = atoms_with_variable(target, var)
            if not atoms_using_var:
                continue
            virtual_target = without_atoms(target, atoms_using_var)
            if self._homomorphism_algorithm.exist_homomorphism(
                FrozenAtomSet(target), virtual_target, pre_sub
            ):
                for atom in atoms_using_var:
                    target.discard(atom)

        return to_same_type(atom_set, target)  # type: ignore[return-value]
