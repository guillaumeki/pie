"""
UnionQuery: A union (disjunction) of queries of the same type.
"""
from functools import cached_property
from typing import Generic, Iterable, Iterator, Optional, TypeVar, TYPE_CHECKING, cast

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.substitution.substitutable import Substitutable
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
    from prototyping_inference_engine.api.query.fo_query import FOQuery

Q = TypeVar("Q", bound=Query)

# Type alias for backward compatibility
# UCQ = UnionQuery[ConjunctiveQuery] - defined at module level after class definition


class UnionQuery(Query, Substitutable["UnionQuery[Q]"], Generic[Q]):
    """
    A union (disjunction) of queries of the same type.

    UnionQuery represents Q1 ∨ Q2 ∨ ... ∨ Qn where each Qi is a query
    of type Q with the same answer variables.

    This is a generalization of UnionConjunctiveQueries that works with
    any query type (ConjunctiveQuery, FOQuery, etc.).

    Example:
        # Union of two conjunctive queries
        ucq = UnionQuery([cq1, cq2], answer_variables=[X, Y])

        # Union of two FO queries
        ufo = UnionQuery([foq1, foq2], answer_variables=[X])
    """

    def __init__(
        self,
        queries: Optional[Iterable[Q]] = None,
        answer_variables: Optional[Iterable[Variable]] = None,
        label: Optional[str] = None,
    ):
        """
        Create a union of queries.

        Args:
            queries: The queries to union (must have compatible answer variables)
            answer_variables: The answer variables for the union
            label: Optional label for the query

        Raises:
            ValueError: If queries have incompatible answer variable counts
        """
        if answer_variables is None:
            answer_variables = ()
        if queries is None:
            queries = []

        Query.__init__(self, answer_variables, label)

        # Normalize queries to use the same answer variables
        normalized: list[Q] = []
        for q in queries:
            if len(self.answer_variables) != len(q.answer_variables):
                raise ValueError(
                    f"Query has incompatible number of answer variables: {q} "
                    f"- expected {len(self.answer_variables)}, got {len(q.answer_variables)}"
                )
            # Apply substitution to rename answer variables if needed
            if q.answer_variables != self.answer_variables:
                rename_sub = Substitution({
                    v: t for v, t in zip(q.answer_variables, self.answer_variables)
                })
                if isinstance(q, Substitutable):
                    q = rename_sub.apply(q)
            normalized.append(q)

        self._queries: frozenset[Q] = frozenset(normalized)

    @property
    def queries(self) -> frozenset[Q]:
        """The queries in this union."""
        return self._queries

    @cached_property
    def terms(self) -> set[Term]:
        """All terms appearing in any query of the union."""
        result: set[Term] = set()
        for q in self._queries:
            result.update(q.terms)
        return result

    @cached_property
    def constants(self) -> set[Constant]:
        """All constants appearing in any query of the union."""
        result: set[Constant] = set()
        for q in self._queries:
            result.update(q.constants)
        return result

    @cached_property
    def variables(self) -> set[Variable]:
        """All variables appearing in any query of the union."""
        result: set[Variable] = set()
        for q in self._queries:
            result.update(q.variables)
        return result

    def apply_substitution(self, substitution: Substitution) -> "UnionQuery[Q]":
        """
        Apply a substitution to all queries in the union.

        Note: If a substitution maps answer variables to constants,
        those variables are removed from the answer variables list.
        The sub-queries are applied with the substitution independently.
        """
        new_queries = []
        for q in self._queries:
            if isinstance(q, Substitutable):
                try:
                    new_queries.append(substitution.apply(q))
                except ValueError:
                    # Query may fail validation after substitution
                    # (e.g., answer variable substituted with constant)
                    # Skip this query in the result
                    pass
            else:
                new_queries.append(q)

        new_answer_vars = []
        for v in self.answer_variables:
            result = substitution.apply(v)
            if isinstance(result, Variable):
                new_answer_vars.append(result)
            # Constants are dropped from answer variables

        return UnionQuery(new_queries, new_answer_vars, self._label)

    @property
    def str_without_answer_variables(self) -> str:
        """String representation of the union body."""
        parts = []
        for q in self._queries:
            s = q.str_without_answer_variables
            # Add parentheses if the query representation might be ambiguous
            if len(self._queries) > 1:
                parts.append(f"({s})")
            else:
                parts.append(s)
        return " \u2228 ".join(parts)

    @property
    def conjunctive_queries(self) -> "frozenset[ConjunctiveQuery]":
        """
        Alias for queries property when used with ConjunctiveQuery.

        This property provides backward compatibility with code that used
        UnionConjunctiveQueries.conjunctive_queries.
        """
        return cast("frozenset[ConjunctiveQuery]", self._queries)

    def to_fo_query(self) -> "FOQuery":
        """
        Convert this union of conjunctive queries to a first-order query.

        Each CQ is converted to a formula (conjunction with existential quantifiers),
        then combined with disjunctions.

        Example:
            UCQ: ?(X) :- p(X,Y) | q(X,Z)
            FOQuery: ?(X) :- (∃Y.p(X,Y)) ∨ (∃Z.q(X,Z))

        Raises:
            ValueError: If the union is empty or contains non-ConjunctiveQuery queries
        """
        from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
        from prototyping_inference_engine.api.formula.disjunction_formula import DisjunctionFormula
        from prototyping_inference_engine.api.formula.existential_formula import ExistentialFormula
        from prototyping_inference_engine.api.formula.formula import Formula
        from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
        from prototyping_inference_engine.api.query.fo_query import FOQuery

        if not self._queries:
            raise ValueError("Cannot convert empty UnionQuery to FOQuery")

        def cq_to_formula(cq: ConjunctiveQuery) -> Formula:
            """Convert a single CQ to a formula with existential quantification."""
            atoms_list = list(cq.atoms)
            if not atoms_list:
                raise ValueError("Cannot convert empty conjunctive query")

            # Build conjunction from atoms
            formula: Formula = atoms_list[0]
            for atom in atoms_list[1:]:
                formula = ConjunctionFormula(formula, atom)

            # Wrap in existential quantifiers for non-answer variables
            for var in cq.existential_variables:
                formula = ExistentialFormula(var, formula)

            return formula

        # Convert all queries to formulas
        formulas = []
        for q in self._queries:
            if not isinstance(q, ConjunctiveQuery):
                raise ValueError(
                    f"to_fo_query() only works with ConjunctiveQuery, got {type(q).__name__}"
                )
            formulas.append(cq_to_formula(q))

        # Combine with disjunctions
        combined: Formula = formulas[0]
        for formula in formulas[1:]:
            combined = DisjunctionFormula(combined, formula)

        return FOQuery(combined, self.answer_variables, self._label)

    def __or__(self, other: "UnionQuery[Q]") -> "UnionQuery[Q]":
        """Union two UnionQueries."""
        if self.answer_variables != other.answer_variables:
            raise ValueError(
                f"Cannot union queries with different answer variables: "
                f"{self.answer_variables} vs {other.answer_variables}"
            )
        return UnionQuery(
            self._queries | other._queries,
            self.answer_variables,
            self._label,
        )

    def __iter__(self) -> Iterator[Q]:
        """Iterate over the queries in the union."""
        return iter(self._queries)

    def __len__(self) -> int:
        """Number of queries in the union."""
        return len(self._queries)

    def __eq__(self, other) -> bool:
        if not isinstance(other, UnionQuery):
            return False
        return (
            self._queries == other._queries
            and self.answer_variables == other.answer_variables
            and self._label == other._label
        )

    def __hash__(self) -> int:
        return hash((self._queries, self.answer_variables, self._label))

    def __repr__(self) -> str:
        return f"UnionQuery: {self}"

    def __str__(self) -> str:
        answers = ", ".join(map(str, self.answer_variables))
        return f"({answers}) :- {self.str_without_answer_variables}"


# Type alias for Union of Conjunctive Queries (backward compatibility)
# Usage: UCQ = UnionQuery[ConjunctiveQuery]
# Note: Cannot define here due to circular import, import ConjunctiveQuery first
