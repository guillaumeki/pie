"""
ParseResult dataclass for structured DLGP parsing results.
"""

from dataclasses import dataclass
from typing import FrozenSet, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
    from prototyping_inference_engine.api.ontology.rule.rule import Rule
    from prototyping_inference_engine.api.ontology.constraint.negative_constraint import (
        NegativeConstraint,
    )
    from prototyping_inference_engine.api.query.query import Query
    from prototyping_inference_engine.api.data.readable_data import ReadableData


@dataclass(frozen=True)
class ParseResult:
    """
    Result of parsing DLGP content.

    Contains all parsed elements categorized by type:
    - facts: Ground atoms (the extensional database)
    - rules: Inference rules (the intensional database)
    - queries: Parsed queries (any Query implementation)
    - constraints: Negative constraints
    - sources: Extra readable data sources needed for evaluation
    - base_iri: Parsed @base value (if any)
    - prefixes: Parsed @prefix mappings (if any)

    This class is immutable (frozen dataclass).
    """

    facts: "FrozenAtomSet"
    rules: FrozenSet["Rule"]
    queries: FrozenSet["Query"]
    constraints: FrozenSet["NegativeConstraint"]
    sources: tuple["ReadableData", ...] = ()
    base_iri: str | None = None
    prefixes: tuple[tuple[str, str], ...] = ()

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
