from typing import Optional

from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint
from prototyping_inference_engine.api.ontology.rule.rule import Rule


class Ontology:
    def __init__(
        self,
        rules: Optional[set[Rule]] = None,
        negative_constraints: Optional[set[NegativeConstraint]] = None,
    ):
        self._rules = set(rules) if rules else set()
        self._negative_constraints = set(negative_constraints) if negative_constraints else set()

    @property
    def negative_constraints(self) -> set[NegativeConstraint]:
        return self._negative_constraints

    @property
    def rules(self) -> set[Rule]:
        return self._rules
