"""
Prepared FOQuery implementations used by evaluators.
"""

# References:
# - "Extensions of Simple Conceptual Graphs: the Complexity of Rules and Constraints" —
#   Jean-Francois Baget, Marie-Laure Mugnier.
#   Link: https://doi.org/10.1613/jair.918
#
# Summary:
# Conjunctive query answering can be reduced to projection (graph homomorphism)
# and is typically implemented via backtracking search with pruning heuristics.
#
# Properties used here:
# - Completeness of backtracking projection for conjunctive queries.
#
# Implementation notes:
# This module implements the backtracking evaluation strategy used by prepared
# conjunctive queries.

from __future__ import annotations

from itertools import product
from typing import Iterable, Iterator, Optional, Sequence, TYPE_CHECKING, cast
import warnings

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import SpecialPredicate
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.atomic_pattern import AtomicPattern
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.disjunction_formula import (
    DisjunctionFormula,
)
from prototyping_inference_engine.api.formula.existential_formula import (
    ExistentialFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.formula.negation_formula import NegationFormula
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.query.prepared_fo_query import (
    PreparedFOQuery,
    PreparedFOQueryDefaults,
)
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.query_evaluation.evaluator.errors import (
    UnsupportedFormulaError,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.warnings import (
    UnsafeNegationWarning,
    UniversalQuantifierWarning,
)
from prototyping_inference_engine.query_evaluation.evaluator.rewriting.function_term_rewriter import (
    expand_function_terms,
    formula_contains_function,
    rewrite_atom_function_terms,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.data.readable_data import ReadableData


def _sorted_variables(variables: Iterable[Variable]) -> list[Variable]:
    return sorted(variables, key=lambda v: str(v))


def _query_for_formula(formula: Formula) -> FOQuery:
    return FOQuery(formula, _sorted_variables(formula.free_variables))


class DelegatingPreparedFOQuery(PreparedFOQueryDefaults):
    """Prepared FOQuery that delegates to another prepared query."""

    def __init__(self, query: FOQuery, delegate: PreparedFOQuery):
        self._query = query
        self._delegate = delegate

    @property
    def query(self) -> FOQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._delegate.data_source

    def execute(self, assignation: Substitution) -> Iterable[Substitution]:
        return self._delegate.execute(assignation)

    def is_evaluable_with(self, substitution: Substitution) -> bool:
        return self._delegate.is_evaluable_with(substitution)

    def mandatory_parameters(self) -> set[Variable]:
        return self._delegate.mandatory_parameters()

    def estimate_bound(self, substitution: Substitution) -> int | None:
        return self._delegate.estimate_bound(substitution)


class PreparedAtomicFOQuery(PreparedFOQueryDefaults):
    """Prepared query for atomic formulas."""

    def __init__(self, query: FOQuery[Atom], data_source: "ReadableData"):
        self._query = query
        self._data_source = data_source
        self._atom = query.formula
        self._missing_predicate: bool = not data_source.has_predicate(
            self._atom.predicate
        )
        self._pattern: AtomicPattern
        self._mandatory: set[Variable] = set()
        self._ground_positions: dict[int, Term] = {}
        self._variable_positions: dict[Variable, list[int]] = {}
        try:
            self._pattern = data_source.get_atomic_pattern(self._atom.predicate)
        except KeyError:
            self._missing_predicate = True
            from prototyping_inference_engine.api.data.atomic_pattern import (
                UnconstrainedPattern,
            )

            self._pattern = UnconstrainedPattern(self._atom.predicate)
        if not self._missing_predicate:
            self._mandatory = self._compute_mandatory_parameters()
            self._ground_positions = self._compute_ground_positions()
            self._variable_positions = self._compute_variable_positions()

    @property
    def query(self) -> FOQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._data_source

    def execute(self, assignation: Substitution) -> Iterable[Substitution]:
        if self._missing_predicate:
            return
        query = self._build_basic_query(assignation)
        if query is None:
            return

        if not self._data_source.can_evaluate(query):
            unsatisfied = self._pattern.get_unsatisfied_positions(
                self._atom, assignation
            )
            raise ValueError(
                f"Cannot evaluate atom {self._atom}: "
                f"unsatisfied constraints at positions {unsatisfied}"
            )

        answer_positions = sorted(query.answer_variables.keys())

        for term_tuple in self._data_source.evaluate(query):
            result: dict[Variable, Term] = {}
            consistent = True
            for pos, term in zip(answer_positions, term_tuple):
                var = query.answer_variables[pos]
                if var in result:
                    if result[var] != term:
                        consistent = False
                        break
                else:
                    result[var] = term
            if consistent:
                yield assignation.compose(Substitution(result))

    def estimate_bound(self, substitution: Substitution) -> int | None:
        if self._missing_predicate:
            return 0
        query = self._build_basic_query(substitution)
        if query is None:
            return 0
        if not self._data_source.can_evaluate(query):
            return 0
        return self._data_source.estimate_bound(query)

    def is_evaluable_with(self, substitution: Substitution) -> bool:
        if self._missing_predicate:
            return False
        query = self._build_basic_query(substitution)
        if query is None:
            return False
        return self._data_source.can_evaluate(query)

    def mandatory_parameters(self) -> set[Variable]:
        return set(self._mandatory)

    def _compute_mandatory_parameters(self) -> set[Variable]:
        mandatory: set[Variable] = set()
        for pos, term in enumerate(self._atom.terms):
            constraint = self._pattern.get_constraint(pos)
            if constraint is None:
                continue
            if isinstance(term, Variable):
                mandatory.add(term)
        return mandatory

    def _compute_ground_positions(self) -> dict[int, Term]:
        return {
            pos: term for pos, term in enumerate(self._atom.terms) if term.is_ground
        }

    def _compute_variable_positions(self) -> dict[Variable, list[int]]:
        positions: dict[Variable, list[int]] = {}
        for pos, term in enumerate(self._atom.terms):
            if isinstance(term, Variable):
                positions.setdefault(term, []).append(pos)
        return positions

    def _build_basic_query(self, substitution: Substitution) -> Optional[BasicQuery]:
        bound_positions: dict[int, Term] = dict(self._ground_positions)
        answer_variables: dict[int, Variable] = {}

        for var, positions in self._variable_positions.items():
            resolved = substitution.apply(var)
            if resolved.is_ground:
                for pos in positions:
                    existing = bound_positions.get(pos)
                    if existing is not None and existing != resolved:
                        return None
                    bound_positions[pos] = resolved
            elif isinstance(resolved, Variable):
                for pos in positions:
                    answer_variables[pos] = resolved

        return BasicQuery(self._atom.predicate, bound_positions, answer_variables)


class PreparedBacktrackingConjunctiveFOQuery(PreparedFOQueryDefaults):
    """Prepared query for conjunction formulas using backtracking."""

    def __init__(self, query: FOQuery[ConjunctionFormula], data_source: "ReadableData"):
        self._query = query
        self._data_source = data_source
        self._formula = query.formula
        self._subqueries: list[PreparedFOQuery] = []
        self._equality_atoms: list[Atom] = []
        self._prepare_subqueries()

    @property
    def query(self) -> FOQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._data_source

    def execute(self, assignation: Substitution) -> Iterable[Substitution]:
        substitution = assignation

        if self._equality_atoms:
            partition = self._build_term_partition(self._equality_atoms, substitution)
            if not partition.is_admissible:
                return []
            equality_sub = partition.associated_substitution()
            if equality_sub is None:
                return []
            substitution = substitution.compose(equality_sub)

        if not self._subqueries:
            return [substitution.normalize()]

        return self._backtrack(substitution, list(self._subqueries))

    def estimate_bound(self, substitution: Substitution) -> int | None:
        bounds = [query.estimate_bound(substitution) for query in self._subqueries]
        if any(bound == 0 for bound in bounds):
            return 0
        if any(bound is None for bound in bounds):
            return None
        product = 1
        for bound in bounds:
            if bound is None:
                return None
            product *= bound
        return product

    def _prepare_subqueries(self) -> None:
        sub_formulas = _flatten_conjunction(self._formula)
        sub_formulas = expand_function_terms(sub_formulas)
        equality_atoms, other_formulas = _separate_equalities(sub_formulas)
        self._equality_atoms = equality_atoms

        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
            FOQueryEvaluatorRegistry,
        )

        registry = FOQueryEvaluatorRegistry.instance()
        for formula in other_formulas:
            prepared = _prepare_formula(formula, self._data_source, registry)
            self._subqueries.append(prepared)

    def _backtrack(
        self,
        substitution: Substitution,
        remaining: list[PreparedFOQuery],
    ) -> Iterator[Substitution]:
        if not remaining:
            yield substitution.normalize()
            return

        next_index = _select_next_query_index(remaining, substitution)
        next_query = remaining[next_index]
        next_remaining = list(remaining)
        next_remaining.pop(next_index)

        for extended_sub in next_query.execute(substitution):
            yield from self._backtrack(extended_sub, next_remaining)

    def _build_term_partition(
        self, equality_atoms: list[Atom], substitution: Substitution
    ) -> TermPartition:
        partition = TermPartition()
        for atom in equality_atoms:
            t1 = substitution.apply(atom.terms[0])
            t2 = substitution.apply(atom.terms[1])
            partition.union(t1, t2)
        return partition


class PreparedDisjunctiveFOQuery(PreparedFOQueryDefaults):
    """Prepared query for disjunction formulas."""

    def __init__(self, query: FOQuery[DisjunctionFormula], data_source: "ReadableData"):
        self._query = query
        self._data_source = data_source
        self._formula = query.formula
        self._left = self._prepare_side(self._formula.left)
        self._right = self._prepare_side(self._formula.right)

    @property
    def query(self) -> FOQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._data_source

    def execute(self, assignation: Substitution) -> Iterable[Substitution]:
        seen = set()
        for result_sub in self._left.execute(assignation):
            key = frozenset(result_sub.items())
            if key not in seen:
                seen.add(key)
                yield result_sub
        for result_sub in self._right.execute(assignation):
            key = frozenset(result_sub.items())
            if key not in seen:
                seen.add(key)
                yield result_sub

    def estimate_bound(self, substitution: Substitution) -> int | None:
        left = self._left.estimate_bound(substitution)
        right = self._right.estimate_bound(substitution)
        if left is None or right is None:
            return None
        return left + right

    def is_evaluable_with(self, substitution: Substitution) -> bool:
        return self._left.is_evaluable_with(
            substitution
        ) or self._right.is_evaluable_with(substitution)

    def _prepare_side(self, formula: Formula) -> PreparedFOQuery:
        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
            FOQueryEvaluatorRegistry,
        )

        registry = FOQueryEvaluatorRegistry.instance()
        answer_vars = [
            var for var in self._query.answer_variables if var in formula.free_variables
        ]
        query = FOQuery(formula, answer_vars)
        evaluator = registry.get_evaluator(query)
        if evaluator is None:
            raise UnsupportedFormulaError(type(formula))
        return evaluator.prepare(query, self._data_source)


class PreparedNegationFOQuery(PreparedFOQueryDefaults):
    """Prepared query for negation formulas."""

    def __init__(self, query: FOQuery[NegationFormula], data_source: "ReadableData"):
        self._query = query
        self._data_source = data_source
        self._formula = query.formula
        self._inner = self._prepare_inner(self._formula.inner)

    @property
    def query(self) -> FOQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._data_source

    def execute(self, assignation: Substitution) -> Iterable[Substitution]:
        inner = self._formula.inner
        inner_free_vars = inner.free_variables
        bound_vars = set(assignation.domain)
        unbound_vars = set(inner_free_vars - bound_vars)

        if not unbound_vars:
            for _ in self._inner.execute(assignation):
                return []
            return [assignation]

        warnings.warn(
            f"Unsafe negation: variables {unbound_vars} are free in negated formula. "
            "Iterating over the entire domain. This may be slow for large data sources.",
            UnsafeNegationWarning,
            stacklevel=3,
        )

        if not hasattr(self._data_source, "terms"):
            raise ValueError(
                "Cannot evaluate unsafe negation: data source does not support "
                "term enumeration. Use a safe negation pattern instead."
            )

        domain = self._data_source.terms
        if not domain:
            return []

        results: list[Substitution] = []
        unbound_vars_list = list(unbound_vars)
        for assignment in product(domain, repeat=len(unbound_vars_list)):
            var_assignment = dict(zip(unbound_vars_list, assignment))
            extended_sub = assignation.compose(Substitution(var_assignment))
            has_result = False
            for _ in self._inner.execute(extended_sub):
                has_result = True
                break
            if not has_result:
                results.append(extended_sub)
        return results

    def estimate_bound(self, substitution: Substitution) -> int | None:
        return 1

    def is_evaluable_with(self, substitution: Substitution) -> bool:
        inner_free_vars = self._formula.inner.free_variables
        return inner_free_vars.issubset(set(substitution.domain))

    def _prepare_inner(self, formula: Formula) -> PreparedFOQuery:
        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
            FOQueryEvaluatorRegistry,
        )

        registry = FOQueryEvaluatorRegistry.instance()
        query = FOQuery(formula, list(self._query.answer_variables))
        evaluator = registry.get_evaluator(query)
        if evaluator is None:
            raise UnsupportedFormulaError(type(formula))
        return evaluator.prepare(query, self._data_source)


class PreparedExistentialFOQuery(PreparedFOQueryDefaults):
    """Prepared query for existential formulas."""

    def __init__(self, query: FOQuery[ExistentialFormula], data_source: "ReadableData"):
        self._query = query
        self._data_source = data_source
        self._formula = query.formula
        self._inner = self._prepare_inner(self._formula.inner)
        self._bound_var = self._formula.variable

    @property
    def query(self) -> FOQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._data_source

    def execute(self, assignation: Substitution) -> Iterable[Substitution]:
        seen = set()
        for result_sub in self._inner.execute(assignation):
            projected = Substitution(
                {k: v for k, v in result_sub.items() if k != self._bound_var}
            )
            key = frozenset(projected.items())
            if key not in seen:
                seen.add(key)
                yield projected

    def estimate_bound(self, substitution: Substitution) -> int | None:
        return self._inner.estimate_bound(substitution)

    def is_evaluable_with(self, substitution: Substitution) -> bool:
        return self._inner.is_evaluable_with(substitution)

    def _prepare_inner(self, formula: Formula) -> PreparedFOQuery:
        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
            FOQueryEvaluatorRegistry,
        )

        registry = FOQueryEvaluatorRegistry.instance()
        query = FOQuery(formula, _sorted_variables(formula.free_variables))
        evaluator = registry.get_evaluator(query)
        if evaluator is None:
            raise UnsupportedFormulaError(type(formula))
        return evaluator.prepare(query, self._data_source)


class PreparedUniversalFOQuery(PreparedFOQueryDefaults):
    """Prepared query for universal formulas."""

    def __init__(self, query: FOQuery[UniversalFormula], data_source: "ReadableData"):
        self._query = query
        self._data_source = data_source
        self._formula = query.formula
        self._inner = self._prepare_inner(self._formula.inner)
        self._bound_var = self._formula.variable

    @property
    def query(self) -> FOQuery:
        return self._query

    @property
    def data_source(self) -> "ReadableData":
        return self._data_source

    def execute(self, assignation: Substitution) -> Iterable[Substitution]:
        if not hasattr(self._data_source, "terms"):
            raise ValueError(
                "Cannot evaluate universal quantifier: data source does not support "
                "term enumeration."
            )

        domain = self._data_source.terms
        if not domain:
            return [assignation]

        warnings.warn(
            f"Universal quantifier ∀{self._bound_var}: iterating over domain "
            f"({len(domain)} terms). This may be slow for large data sources.",
            UniversalQuantifierWarning,
            stacklevel=3,
        )

        inner_formula = self._formula.inner
        other_free_vars = inner_formula.free_variables - {self._bound_var}
        has_other_free_vars = bool(other_free_vars - set(assignation.domain))

        if not has_other_free_vars:
            for term in domain:
                extended_sub = assignation.compose(
                    Substitution({self._bound_var: term})
                )
                has_result = False
                for _ in self._inner.execute(extended_sub):
                    has_result = True
                    break
                if not has_result:
                    return []
            return [assignation]

        valid_subs: Optional[set[tuple[tuple[Variable, Term], ...]]] = None

        for term in domain:
            extended_sub = assignation.compose(Substitution({self._bound_var: term}))
            results: set[tuple[tuple[Variable, Term], ...]] = set()
            for result_sub in self._inner.execute(extended_sub):
                filtered = Substitution(
                    {k: v for k, v in result_sub.items() if k != self._bound_var}
                )
                results.add(tuple(sorted(filtered.items())))

            if valid_subs is None:
                valid_subs = results
            else:
                valid_subs = valid_subs & results

            if not valid_subs:
                return []

        if not valid_subs:
            return []

        return [Substitution(dict(sub_tuple)) for sub_tuple in valid_subs]

    def estimate_bound(self, substitution: Substitution) -> int | None:
        return self._inner.estimate_bound(substitution)

    def is_evaluable_with(self, substitution: Substitution) -> bool:
        return True

    def _prepare_inner(self, formula: Formula) -> PreparedFOQuery:
        from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
            FOQueryEvaluatorRegistry,
        )

        registry = FOQueryEvaluatorRegistry.instance()
        query = FOQuery(formula, _sorted_variables(formula.free_variables))
        evaluator = registry.get_evaluator(query)
        if evaluator is None:
            raise UnsupportedFormulaError(type(formula))
        return evaluator.prepare(query, self._data_source)


def prepare_atomic_or_conjunction(
    query: FOQuery[Atom], data_source: "ReadableData"
) -> PreparedFOQuery:
    atom = query.formula
    if formula_contains_function(atom):
        rewritten_atoms = rewrite_atom_function_terms(atom)
        if len(rewritten_atoms) > 1:
            conjunction = _build_conjunction(rewritten_atoms)
            rewritten_query = FOQuery(
                conjunction, _sorted_variables(conjunction.free_variables)
            )
            from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluator_registry import (
                FOQueryEvaluatorRegistry,
            )

            registry = FOQueryEvaluatorRegistry.instance()
            evaluator = registry.get_evaluator(rewritten_query)
            if evaluator is None:
                raise UnsupportedFormulaError(type(conjunction))
            prepared = evaluator.prepare(rewritten_query, data_source)
            return DelegatingPreparedFOQuery(query, prepared)
    return PreparedAtomicFOQuery(query, data_source)


def _prepare_formula(
    formula: Formula, data_source: "ReadableData", registry
) -> PreparedFOQuery:
    query = _query_for_formula(formula)
    evaluator = registry.get_evaluator(query)
    if evaluator is None:
        raise UnsupportedFormulaError(type(formula))
    return evaluator.prepare(query, data_source)


def _build_conjunction(formulas: list[Atom]) -> ConjunctionFormula:
    if not formulas:
        raise ValueError("Cannot build conjunction from empty formula list.")
    current: Formula = formulas[0]
    for next_formula in formulas[1:]:
        current = ConjunctionFormula(current, next_formula)
    return cast(ConjunctionFormula, current)


def _flatten_conjunction(formula: ConjunctionFormula) -> list[Formula]:
    result: list[Formula] = []
    if isinstance(formula.left, ConjunctionFormula):
        result.extend(_flatten_conjunction(formula.left))
    else:
        result.append(formula.left)
    if isinstance(formula.right, ConjunctionFormula):
        result.extend(_flatten_conjunction(formula.right))
    else:
        result.append(formula.right)
    return result


def _separate_equalities(
    formulas: list[Formula],
) -> tuple[list[Atom], list[Formula]]:
    equality_atoms: list[Atom] = []
    other_formulas: list[Formula] = []
    for formula in formulas:
        if (
            isinstance(formula, Atom)
            and formula.predicate == SpecialPredicate.EQUALITY.value
        ):
            equality_atoms.append(formula)
        else:
            other_formulas.append(formula)
    return equality_atoms, other_formulas


def _select_next_query_index(
    queries: Sequence[PreparedFOQuery], substitution: Substitution
) -> int:
    candidates: list[tuple[float, int]] = []
    for index, query in enumerate(queries):
        if not query.is_evaluable_with(substitution):
            continue
        bound = query.estimate_bound(substitution)
        score = float("inf") if bound is None else float(bound)
        candidates.append((score, index))
    if candidates:
        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][1]
    return 0
