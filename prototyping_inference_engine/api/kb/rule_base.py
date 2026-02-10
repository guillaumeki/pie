from typing import Optional

from prototyping_inference_engine.api.ontology.constraint.negative_constraint import (
    NegativeConstraint,
)
from prototyping_inference_engine.api.ontology.rule.rule import Rule


class RuleBase:
    """
    Container for rules and negative constraints.
    """

    def __init__(
        self,
        rules: Optional[set[Rule]] = None,
        negative_constraints: Optional[set[NegativeConstraint]] = None,
    ):
        self._rules = set(rules) if rules else set()
        self._negative_constraints = (
            set(negative_constraints) if negative_constraints else set()
        )

    @property
    def rules(self) -> set[Rule]:
        return self._rules

    @property
    def negative_constraints(self) -> set[NegativeConstraint]:
        return self._negative_constraints

    def add_rule(self, rule: Rule) -> None:
        self._rules.add(rule)

    def add_negative_constraint(self, constraint: NegativeConstraint) -> None:
        self._negative_constraints.add(constraint)
