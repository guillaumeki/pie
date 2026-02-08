from typing import Optional

from prototyping_inference_engine.api.kb.rule_base import RuleBase
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import (
    NegativeConstraint,
)
from prototyping_inference_engine.api.ontology.rule.rule import Rule


class Ontology(RuleBase):
    def __init__(
        self,
        rules: Optional[set[Rule]] = None,
        negative_constraints: Optional[set[NegativeConstraint]] = None,
    ):
        super().__init__(rules=rules, negative_constraints=negative_constraints)
