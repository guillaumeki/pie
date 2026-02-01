"""
Backtracking-based conjunction evaluator.
"""
from typing import Iterator, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import SpecialPredicate
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
from prototyping_inference_engine.query_evaluation.evaluator.conjunction.conjunction_evaluator import ConjunctionEvaluator
from prototyping_inference_engine.query_evaluation.evaluator.conjunction.scheduler.formula_scheduler import FormulaScheduler
from prototyping_inference_engine.query_evaluation.evaluator.conjunction.scheduler.formula_scheduler_provider import (
    FormulaSchedulerProvider,
    SequentialSchedulerProvider,
)
from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator import RegistryMixin
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData
    from prototyping_inference_engine.query_evaluation.evaluator.formula_evaluator_registry import FormulaEvaluatorRegistry


class BacktrackConjunctionEvaluator(RegistryMixin, ConjunctionEvaluator):
    """
    Evaluates conjunction formulas using a backtracking algorithm.

    The evaluator flattens nested conjunctions and uses a scheduler to
    determine the order in which sub-formulas are evaluated. For each
    sub-formula, it delegates to the appropriate evaluator from the registry.

    Example:
        For formula (p(X,Y) ∧ q(Y)) ∧ r(X):
        1. Flatten to [p(X,Y), q(Y), r(X)]
        2. Evaluate p(X,Y) → yields {X→a, Y→b}
        3. Evaluate q(Y) with {X→a, Y→b} → yields {X→a, Y→b}
        4. Evaluate r(X) with {X→a, Y→b} → yields {X→a, Y→b}
        5. Final result: {X→a, Y→b}
    """

    def __init__(
        self,
        registry: Optional["FormulaEvaluatorRegistry"] = None,
        scheduler_provider: Optional[FormulaSchedulerProvider] = None,
    ):
        """
        Create a backtracking conjunction evaluator.

        Args:
            registry: The formula evaluator registry. If None, uses the singleton.
            scheduler_provider: Provider for formula schedulers.
                               Defaults to SequentialSchedulerProvider.
        """
        RegistryMixin.__init__(self, registry)
        self._scheduler_provider = scheduler_provider or SequentialSchedulerProvider()

    def evaluate(
        self,
        formula: ConjunctionFormula,
        data: "ReadableData",
        substitution: Substitution = None,
    ) -> Iterator[Substitution]:
        """
        Evaluate a conjunction formula against a data source.

        Equality atoms (X = Y) are extracted and transformed into a TermPartition
        to handle transitive equalities correctly. The associated substitution
        is computed and applied before evaluating non-equality atoms.

        Args:
            formula: The conjunction formula to evaluate
            data: The data source to query
            substitution: An optional initial substitution

        Yields:
            All substitutions that satisfy the conjunction
        """
        if substitution is None:
            substitution = Substitution()

        # Flatten the conjunction into a list of sub-formulas
        sub_formulas = self._flatten_conjunction(formula)

        # Separate equality atoms from other formulas
        equality_atoms, other_formulas = self._separate_equalities(sub_formulas)

        # Build TermPartition from equality atoms
        if equality_atoms:
            partition = self._build_term_partition(equality_atoms, substitution)

            # Check if partition is admissible (no two different constants in same class)
            if not partition.is_admissible:
                # Inconsistent equalities, no solutions
                return

            # Get the substitution from the partition
            equality_sub = partition.associated_substitution()
            if equality_sub is None:
                # Inconsistent partition
                return

            # Compose with initial substitution
            substitution = substitution.compose(equality_sub)

        # If no other formulas, yield the substitution from equalities
        if not other_formulas:
            yield substitution.normalize()
            return

        # Create a scheduler for non-equality formulas
        scheduler = self._scheduler_provider.create_scheduler(other_formulas)

        # Run backtracking
        yield from self._backtrack(data, substitution, scheduler, level=0)

    def _separate_equalities(
        self, formulas: list[Formula]
    ) -> tuple[list[Atom], list[Formula]]:
        """
        Separate equality atoms from other formulas.

        Args:
            formulas: List of formulas to separate

        Returns:
            Tuple of (equality_atoms, other_formulas)
        """
        equality_atoms: list[Atom] = []
        other_formulas: list[Formula] = []

        for f in formulas:
            if (isinstance(f, Atom)
                and f.predicate == SpecialPredicate.EQUALITY.value):
                equality_atoms.append(f)
            else:
                other_formulas.append(f)

        return equality_atoms, other_formulas

    def _build_term_partition(
        self, equality_atoms: list[Atom], substitution: Substitution
    ) -> TermPartition:
        """
        Build a TermPartition from equality atoms.

        Each equality atom X = Y creates a union of the classes containing X and Y.
        The substitution is applied to terms before adding to the partition.

        Args:
            equality_atoms: List of equality atoms
            substitution: Current substitution to apply

        Returns:
            A TermPartition representing all equalities
        """
        partition = TermPartition()

        for atom in equality_atoms:
            # Apply current substitution to terms
            t1 = substitution.apply(atom.terms[0])
            t2 = substitution.apply(atom.terms[1])

            # Union the classes
            partition.union(t1, t2)

        return partition

    def _flatten_conjunction(self, formula: ConjunctionFormula) -> list[Formula]:
        """
        Flatten nested conjunctions into a list of sub-formulas.

        For (p ∧ q) ∧ r, returns [p, q, r].
        For p ∧ (q ∧ r), returns [p, q, r].
        For (p ∧ q) ∧ (r ∧ s), returns [p, q, r, s].
        """
        result: list[Formula] = []

        if isinstance(formula.left, ConjunctionFormula):
            result.extend(self._flatten_conjunction(formula.left))
        else:
            result.append(formula.left)

        if isinstance(formula.right, ConjunctionFormula):
            result.extend(self._flatten_conjunction(formula.right))
        else:
            result.append(formula.right)

        return result

    def _backtrack(
        self,
        data: "ReadableData",
        substitution: Substitution,
        scheduler: FormulaScheduler,
        level: int,
    ) -> Iterator[Substitution]:
        """
        Recursive backtracking algorithm.

        Args:
            data: The data source to query
            substitution: The current substitution
            scheduler: The formula scheduler
            level: The current backtracking level

        Yields:
            All substitutions that satisfy all remaining formulas
        """
        if not scheduler.has_next(level):
            # All sub-formulas have been satisfied
            # Normalize to resolve any variable chains (e.g., X→Y, Y→a becomes X→a, Y→a)
            yield substitution.normalize()
        else:
            # Get the next formula to evaluate
            next_formula = scheduler.next_formula(substitution, level)

            # Get the appropriate evaluator for this formula type
            evaluator = self._get_registry().get_evaluator(next_formula)

            if evaluator is None:
                from prototyping_inference_engine.query_evaluation.evaluator.fo_query_evaluator import (
                    UnsupportedFormulaError,
                )
                raise UnsupportedFormulaError(type(next_formula))

            # Evaluate the formula and recurse for each result
            for extended_sub in evaluator.evaluate(next_formula, data, substitution):
                yield from self._backtrack(data, extended_sub, scheduler, level + 1)
