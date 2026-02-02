"""
Basic query for querying data sources.
"""
from typing import Mapping, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.predicate import Predicate
    from prototyping_inference_engine.api.atom.term.term import Term
    from prototyping_inference_engine.api.atom.term.variable import Variable
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class BasicQuery:
    """
    A simple query specifying a predicate, bound positions, and answer variables.

    BasicQuery represents a query to a data source: "Give me all facts for
    predicate P where position i has value Ti, and return values for the
    answer variables at other positions."

    This is distinct from an Atom: an Atom is a logical formula with terms
    at all positions, while a BasicQuery separates bound positions (filter
    criteria) from answer positions (what to return).
    """

    def __init__(
        self,
        predicate: "Predicate",
        bound_positions: Optional[Mapping[int, "Term"]] = None,
        answer_variables: Optional[Mapping[int, "Variable"]] = None
    ):
        """
        Create a basic query.

        Args:
            predicate: The predicate to query
            bound_positions: Mapping from position index to the term that
                           must appear at that position (filter criteria).
            answer_variables: Mapping from position index to the variable
                            that should receive the value at that position.
        """
        self._predicate = predicate
        self._bound_positions: dict[int, "Term"] = dict(bound_positions) if bound_positions else {}
        self._answer_variables: dict[int, "Variable"] = dict(answer_variables) if answer_variables else {}

    @property
    def predicate(self) -> "Predicate":
        """The predicate being queried."""
        return self._predicate

    @property
    def bound_positions(self) -> Mapping[int, "Term"]:
        """Positions with bound terms (filter criteria)."""
        return self._bound_positions

    @property
    def answer_variables(self) -> Mapping[int, "Variable"]:
        """Positions with answer variables (what to return)."""
        return self._answer_variables

    def get_bound_term(self, position: int) -> Optional["Term"]:
        """Get the bound term at a position, or None if not bound."""
        return self._bound_positions.get(position)

    def get_answer_variable(self, position: int) -> Optional["Variable"]:
        """Get the answer variable at a position, or None if not an answer."""
        return self._answer_variables.get(position)

    def is_bound(self, position: int) -> bool:
        """Check if a position is bound."""
        return position in self._bound_positions

    def is_answer(self, position: int) -> bool:
        """Check if a position has an answer variable."""
        return position in self._answer_variables

    @classmethod
    def from_atom(
        cls,
        atom: "Atom",
        substitution: Optional["Substitution"] = None
    ) -> "BasicQuery":
        """
        Create a BasicQuery from an atom and substitution.

        Positions with ground terms (after applying substitution) become
        bound positions. Positions with unbound variables become answer
        positions.

        Args:
            atom: The atom to convert
            substitution: Optional substitution to apply first

        Returns:
            A BasicQuery with ground positions as bound, variables as answers
        """
        from prototyping_inference_engine.api.substitution.substitution import Substitution
        from prototyping_inference_engine.api.atom.term.variable import Variable

        sub = substitution or Substitution()
        bound_positions = {}
        answer_variables = {}

        for pos, term in enumerate(atom.terms):
            resolved = sub.apply(term)
            if resolved.is_ground:
                bound_positions[pos] = resolved
            elif isinstance(resolved, Variable):
                answer_variables[pos] = resolved

        return cls(atom.predicate, bound_positions, answer_variables)

    def __repr__(self) -> str:
        parts = [str(self._predicate)]
        if self._bound_positions:
            bound_str = ", ".join(
                f"{pos}={term}" for pos, term in sorted(self._bound_positions.items())
            )
            parts.append(f"bound={{{bound_str}}}")
        if self._answer_variables:
            answer_str = ", ".join(
                f"{pos}:{var}" for pos, var in sorted(self._answer_variables.items())
            )
            parts.append(f"answers={{{answer_str}}}")
        return f"BasicQuery({', '.join(parts)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BasicQuery):
            return NotImplemented
        return (
            self._predicate == other._predicate
            and self._bound_positions == other._bound_positions
            and self._answer_variables == other._answer_variables
        )

    def __hash__(self) -> int:
        return hash((
            self._predicate,
            frozenset(self._bound_positions.items()),
            frozenset(self._answer_variables.items())
        ))
