from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint
from prototyping_inference_engine.api.ontology.rule.rule import Rule


class Ontology:
    def __init__(self, rules: set[Rule] = None, negative_constraints: set[NegativeConstraint] = None):
        self._rules = rules if rules else {}
        self._negative_constraints = negative_constraints if negative_constraints else {}

    @property
    def negative_constraints(self) -> set[NegativeConstraint]:
        return self._negative_constraints

    @property
    def rules(self) -> set[Rule]:
        return self._rules
