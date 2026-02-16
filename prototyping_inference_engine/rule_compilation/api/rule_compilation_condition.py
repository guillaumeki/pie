"""
Rule compilation condition interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.substitution.substitution import Substitution


class RuleCompilationCondition(ABC):
    """
    A RuleCompilationCondition represents a compilation condition in the sense
    of Melanie Konig's thesis.
    """

    @abstractmethod
    def check(self, atom_body: Atom, atom_head: Atom) -> bool:
        """Return True iff this condition applies for atom_body <= atom_head."""
        raise NotImplementedError

    @abstractmethod
    def instantiate(
        self, head_terms: Iterable[Term]
    ) -> tuple[list[Term], Substitution] | None:
        """
        Instantiate the condition with the head terms.

        Returns the generated body terms and a substitution representing the
        specialization from the unification with the compiled rule.
        """
        raise NotImplementedError

    @abstractmethod
    def compose_with(
        self, other: "RuleCompilationCondition"
    ) -> "RuleCompilationCondition | None":
        """Compose this condition with another condition."""
        raise NotImplementedError

    @abstractmethod
    def is_identity(self) -> bool:
        """Return True iff this condition is an identity condition."""
        raise NotImplementedError

    @abstractmethod
    def homomorphism(
        self,
        head_terms: Iterable[Term],
        to_terms: Iterable[Term],
        initial_substitution: Substitution,
    ) -> Substitution | None:
        """
        Compute the homomorphism from head_terms to to_terms with respect to
        the initial substitution, assuming the condition applies.
        """
        raise NotImplementedError

    @abstractmethod
    def unifier(self, atom_body: Atom, atom_head: Atom) -> TermPartition | None:
        """Compute the unifier between two atoms, assuming the condition applies."""
        raise NotImplementedError
