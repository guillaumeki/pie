"""
ParseResult dataclass for structured DLGP parsing results.
"""
from dataclasses import dataclass
from typing import FrozenSet, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
    from prototyping_inference_engine.api.ontology.rule.rule import Rule
    from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint
    from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
    from prototyping_inference_engine.api.query.union_query import UnionQuery


@dataclass(frozen=True)
class ParseResult:
    """
    Result of parsing DLGP content.

    Contains all parsed elements categorized by type:
    - facts: Ground atoms (the extensional database)
    - rules: Inference rules (the intensional database)
    - queries: Conjunctive or union of conjunctive queries
    - constraints: Negative constraints

    This class is immutable (frozen dataclass).
    """

    facts: "FrozenAtomSet"
    rules: FrozenSet["Rule"]
    queries: FrozenSet[Union["ConjunctiveQuery", "UnionQuery[ConjunctiveQuery]"]]
    constraints: FrozenSet["NegativeConstraint"]

    @property
    def is_empty(self) -> bool:
        """
        Return True if no content was parsed.

        Returns:
            True if all collections are empty
        """
        return (
            len(self.facts) == 0
            and len(self.rules) == 0
            and len(self.queries) == 0
            and len(self.constraints) == 0
        )

    @property
    def has_facts(self) -> bool:
        """Return True if facts were parsed."""
        return len(self.facts) > 0

    @property
    def has_rules(self) -> bool:
        """Return True if rules were parsed."""
        return len(self.rules) > 0

    @property
    def has_queries(self) -> bool:
        """Return True if queries were parsed."""
        return len(self.queries) > 0

    @property
    def has_constraints(self) -> bool:
        """Return True if constraints were parsed."""
        return len(self.constraints) > 0
