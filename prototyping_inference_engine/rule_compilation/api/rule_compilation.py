"""
Rule compilation interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.rule_compilation.api.rule_compilation_result import (
    RuleCompilationResult,
)


class RuleCompilation(ABC):
    """
    A compilation structure as defined in the Graal/Integraal lineage.
    """

    @abstractmethod
    def compile(self, rule_base: RuleBase) -> None:
        """Compile rules in-place (compiled rules are removed from the rule base)."""
        raise NotImplementedError

    @abstractmethod
    def compile_and_get(self, rule_base: RuleBase) -> RuleCompilationResult:
        """Compile rules and return a result object with partitions."""
        raise NotImplementedError

    @abstractmethod
    def is_more_specific_than(self, atom_a: Atom, atom_b: Atom) -> bool:
        """Return True iff atom_a <= atom_b under this compilation."""
        raise NotImplementedError

    @abstractmethod
    def unfold(self, atom: Atom) -> list[tuple[Atom, Substitution]]:
        """
        Return the unfolding of an atom as (atom, substitution) pairs.

        The substitution represents the specialization from the unification with
        the compiled rule.
        """
        raise NotImplementedError

    @abstractmethod
    def is_compatible(self, pred_p: Predicate, pred_q: Predicate) -> bool:
        """Return True iff predicates are compatible under this compilation."""
        raise NotImplementedError

    @abstractmethod
    def get_compatible_predicates(self, pred: Predicate) -> set[Predicate]:
        """Return the set of predicates compatible with pred."""
        raise NotImplementedError

    def get_homomorphisms(
        self, atom_a: Atom, atom_b: Atom, substitution: Substitution | None = None
    ) -> list[Substitution]:
        return self.get_homomorphisms_with_substitution(
            atom_a, atom_b, substitution or Substitution()
        )

    @abstractmethod
    def get_homomorphisms_with_substitution(
        self, atom_a: Atom, atom_b: Atom, substitution: Substitution
    ) -> list[Substitution]:
        """Compute all homomorphisms from atom_a to atom_b with respect to substitution."""
        raise NotImplementedError

    @abstractmethod
    def get_unifications(self, atom_a: Atom, atom_b: Atom) -> set[TermPartition]:
        """Compute all possible unifications between atom_a and atom_b."""
        raise NotImplementedError
