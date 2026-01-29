"""
Evaluator for atomic formulas.
"""
from typing import Type, Iterator, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm_provider import (
    HomomorphismAlgorithmProvider,
    DefaultHomomorphismAlgorithmProvider,
)
from prototyping_inference_engine.query_processing.evaluator.formula_evaluator import FormulaEvaluator
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.fact_base import FactBase


class AtomEvaluator(FormulaEvaluator[Atom]):
    """
    Evaluates atomic formulas using homomorphism computation.

    For an atom p(X, Y) and a fact base {p(a, b), p(a, c)}, this evaluator
    yields substitutions {X -> a, Y -> b} and {X -> a, Y -> c}.
    """

    def __init__(
        self,
        homomorphism_provider: HomomorphismAlgorithmProvider = None,
    ):
        """
        Create an atom evaluator.

        Args:
            homomorphism_provider: Provider for the homomorphism algorithm.
                                   Defaults to DefaultHomomorphismAlgorithmProvider.
        """
        self._provider = homomorphism_provider or DefaultHomomorphismAlgorithmProvider()

    @classmethod
    def supported_formula_type(cls) -> Type[Atom]:
        return Atom

    def evaluate(
        self,
        formula: Atom,
        fact_base: "FactBase",
        substitution: Substitution = None,
    ) -> Iterator[Substitution]:
        """
        Evaluate an atomic formula against a fact base.

        Finds all homomorphisms from the atom to the fact base atoms,
        yielding each substitution that maps the atom's variables to
        constants in the fact base.

        Args:
            formula: The atom to evaluate
            fact_base: The fact base to query
            substitution: An optional initial substitution

        Yields:
            All substitutions that map the atom to a fact in the fact base
        """
        algorithm = self._provider.get_algorithm()
        query_atoms = FrozenAtomSet([formula])
        fact_atoms = FrozenAtomSet(fact_base)

        initial_sub = substitution if substitution is not None else Substitution()

        yield from algorithm.compute_homomorphisms(
            query_atoms, fact_atoms, initial_sub
        )
