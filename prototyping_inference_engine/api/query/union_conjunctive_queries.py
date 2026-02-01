from functools import reduce
from typing import Iterable, Iterator, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution

if TYPE_CHECKING:
    from prototyping_inference_engine.api.query.fo_query import FOQuery


class UnionConjunctiveQueries(UnionQuery[ConjunctiveQuery]):
    """
    A union (disjunction) of conjunctive queries.

    This is a specialized subclass of UnionQuery[ConjunctiveQuery] that provides
    backward compatibility with the legacy API including the `conjunctive_queries`
    property and `to_fo_query()` method.

    Note: For new code, consider using UnionQuery[ConjunctiveQuery] directly.
    """

    def __init__(
        self,
        cqs: Iterable[ConjunctiveQuery] = None,
        answer_variables: Iterable[Variable] = None,
        label: Optional[str] = None,
    ):
        super().__init__(cqs, answer_variables, label)

    @property
    def conjunctive_queries(self) -> frozenset[ConjunctiveQuery]:
        """Alias for queries property for backward compatibility."""
        return self._queries

    def to_fo_query(self) -> "FOQuery":
        """
        Convert this union of conjunctive queries to a first-order query.

        Each CQ is converted to a formula (conjunction with existential quantifiers),
        then combined with disjunctions.

        Example:
            UCQ: ?(X) :- p(X,Y) | q(X,Z)
            FOQuery: ?(X) :- (∃Y.p(X,Y)) ∨ (∃Z.q(X,Z))
        """
        from prototyping_inference_engine.api.formula.conjunction_formula import ConjunctionFormula
        from prototyping_inference_engine.api.formula.disjunction_formula import DisjunctionFormula
        from prototyping_inference_engine.api.formula.existential_formula import ExistentialFormula
        from prototyping_inference_engine.api.formula.formula import Formula
        from prototyping_inference_engine.api.query.fo_query import FOQuery

        if not self._queries:
            raise ValueError("Cannot convert empty UCQ to FOQuery")

        def cq_to_formula(cq: ConjunctiveQuery) -> Formula:
            """Convert a single CQ to a formula with existential quantification."""
            atoms_list = list(cq.atoms)
            if not atoms_list:
                raise ValueError("Cannot convert empty conjunctive query")

            # Build conjunction from atoms
            formula: Formula = reduce(
                lambda acc, atom: ConjunctionFormula(acc, atom),
                atoms_list[1:],
                atoms_list[0]
            )

            # Wrap in existential quantifiers for non-answer variables
            for var in cq.existential_variables:
                formula = ExistentialFormula(var, formula)

            return formula

        # Convert all CQs to formulas
        formulas = [cq_to_formula(cq) for cq in self._queries]

        # Combine with disjunctions
        combined: Formula = reduce(
            lambda acc, f: DisjunctionFormula(acc, f),
            formulas[1:],
            formulas[0]
        )

        return FOQuery(combined, self.answer_variables, self.label)

    def apply_substitution(self, substitution: Substitution) -> "UnionConjunctiveQueries":
        return UnionConjunctiveQueries((substitution(cq) for cq in self.conjunctive_queries),
                                       [substitution(v) for v in self.answer_variables],
                                       self.label)

    @property
    def str_without_answer_variables(self) -> str:
        return " \u2228 ".join("(" + cq.str_without_answer_variables + ")"
                               if len(cq.atoms) != 1 or len(cq.pre_substitution) != 0
                               else cq.str_without_answer_variables
                               for cq in self.conjunctive_queries)

    def __or__(self, other: "UnionConjunctiveQueries") -> "UnionConjunctiveQueries":
        if self.answer_variables != other.answer_variables:
            raise ValueError(f"You can't do the union of two ucqs with distinct answer variables: {self} and {other}")
        return UnionConjunctiveQueries(self.conjunctive_queries | other.conjunctive_queries, self.answer_variables)

    def __eq__(self, other):
        if not isinstance(other, UnionConjunctiveQueries):
            return False
        return (self.conjunctive_queries == other.conjunctive_queries
                and self.answer_variables == other.answer_variables
                and self.label == other.label)

    def __hash__(self):
        return hash((self.conjunctive_queries, self.answer_variables, self.label))

    def __repr__(self):
        return "UCQ: " + str(self)

    def __str__(self):
        return "({}) :- {}".format(
            ", ".join(map(str, self.answer_variables)),
            self.str_without_answer_variables)

    def __iter__(self) -> Iterator[ConjunctiveQuery]:
        return iter(self.conjunctive_queries)

    def __len__(self):
        return len(self.conjunctive_queries)
