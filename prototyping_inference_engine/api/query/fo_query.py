"""
First-Order Query: a query based on a first-order logic formula.
"""
from functools import cached_property
from typing import Optional, Iterable, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.substitution.substitutable import Substitutable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class FOQuery(Query, Substitutable["FOQuery"]):
    """
    A first-order query consisting of a formula and answer variables.

    The answer variables are the variables whose values we are interested in.
    They must be free variables in the formula.

    Example:
        # Query: ?(X) :- ∃Y.(p(X,Y) ∧ q(Y))
        formula = ExistentialFormula(Y, ConjunctionFormula(p_xy, q_y))
        query = FOQuery(formula, answer_variables=[X])
    """

    def __init__(
        self,
        formula: Formula,
        answer_variables: Optional[Iterable[Variable]] = None,
        label: Optional[str] = None,
    ):
        """
        Create a first-order query.

        Args:
            formula: The formula defining the query
            answer_variables: Variables to return (must be free in the formula)
            label: Optional label for the query

        Raises:
            ValueError: If answer variables are not free in the formula
        """
        Query.__init__(self, answer_variables, label)
        self._formula = formula

        # Validate that answer variables are free in the formula
        free_vars = formula.free_variables
        for v in self._answer_variables:
            if v not in free_vars:
                raise ValueError(
                    f"Answer variable {v} is not free in the formula. "
                    f"Free variables are: {free_vars}"
                )

    @property
    def formula(self) -> Formula:
        """The formula defining this query."""
        return self._formula

    @property
    def terms(self) -> set[Term]:
        """All terms appearing in the formula."""
        terms: set[Term] = set()
        for atom in self._formula.atoms:
            terms.update(atom.terms)
        return terms

    @property
    def variables(self) -> set[Variable]:
        """All variables in the formula (free and bound)."""
        return set(self._formula.free_variables | self._formula.bound_variables)

    @property
    def constants(self) -> set[Constant]:
        """All constants in the formula."""
        return {t for t in self.terms if isinstance(t, Constant)}

    @cached_property
    def existential_variables(self) -> set[Variable]:
        """Free variables that are not answer variables."""
        return set(self._formula.free_variables) - set(self._answer_variables)

    @property
    def free_variables(self) -> frozenset[Variable]:
        """Free variables in the formula."""
        return self._formula.free_variables

    @property
    def bound_variables(self) -> frozenset[Variable]:
        """Bound variables in the formula."""
        return self._formula.bound_variables

    @property
    def atoms(self) -> frozenset[Atom]:
        """All atoms in the formula."""
        return self._formula.atoms

    @property
    def is_boolean(self) -> bool:
        """True if this is a boolean query (no answer variables)."""
        return len(self._answer_variables) == 0

    @property
    def is_closed(self) -> bool:
        """True if the formula has no free variables."""
        return self._formula.is_closed

    @property
    def str_without_answer_variables(self) -> str:
        """String representation of the formula without answer variables."""
        return str(self._formula)

    def apply_substitution(self, substitution: "Substitution") -> "FOQuery":
        """
        Apply a substitution to this query.

        The substitution is applied to both the formula and answer variables.
        Only free variables are substituted in the formula.
        """
        new_formula = self._formula.apply_substitution(substitution)
        new_answer_vars = [
            substitution.apply(v) if isinstance(substitution.apply(v), Variable) else v
            for v in self._answer_variables
        ]
        # Filter to only keep Variables (in case substitution mapped to constant)
        new_answer_vars = [v for v in new_answer_vars if isinstance(v, Variable)]
        return FOQuery(new_formula, new_answer_vars, self._label)

    def __eq__(self, other) -> bool:
        if not isinstance(other, FOQuery):
            return False
        return (
            self._formula == other._formula
            and self._answer_variables == other._answer_variables
            and self._label == other._label
        )

    def __hash__(self) -> int:
        return hash((self._formula, self._answer_variables, self._label))

    def __repr__(self) -> str:
        return f"FOQuery: {self}"

    def __str__(self) -> str:
        answers = ", ".join(map(str, self._answer_variables))
        return f"?({answers}) :- {self._formula}"
