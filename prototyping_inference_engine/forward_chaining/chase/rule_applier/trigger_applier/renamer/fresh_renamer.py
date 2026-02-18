"""Fresh variable renamer for existential variables."""

from __future__ import annotations

from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.trigger_renamer import (
    TriggerRenamer,
)


class FreshRenamer(TriggerRenamer):
    def rename_existentials(
        self, rule: Rule, substitution: Substitution
    ) -> Substitution:
        renamed = Substitution(
            {v: Variable.fresh_variable() for v in rule.existential_variables}
        )
        for var in substitution:
            renamed.pop(var, None)
        return renamed.compose(substitution)
