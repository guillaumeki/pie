"""Frontier-based true skolem renamer using logical function terms."""

from __future__ import annotations

from collections import defaultdict

from prototyping_inference_engine.api.atom.term.logical_function_term import (
    LogicalFunctionalTerm,
)
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.rule_applier.substitution_key import (
    substitution_key,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.trigger_renamer import (
    TriggerRenamer,
)


class FrontierTrueSkolem(TriggerRenamer):
    def __init__(self) -> None:
        self._names: dict[
            Rule, dict[tuple[tuple[object, object], ...], dict[Variable, Term]]
        ] = defaultdict(dict)
        self._counters: dict[Rule, int] = defaultdict(int)

    def rename_existentials(
        self, rule: Rule, substitution: Substitution
    ) -> Substitution:
        frontier = Substitution(
            {
                v: substitution.apply(v)
                for v in rule.frontier
                if substitution.apply(v) != v
            }
        )
        by_sub = self._names[rule].setdefault(substitution_key(frontier), {})
        renamed = Substitution()
        for var in rule.existential_variables:
            if var not in by_sub:
                self._counters[rule] += 1
                args = tuple(frontier.values())
                by_sub[var] = LogicalFunctionalTerm(
                    f"sk_frontier_{rule.label or 'anon'}_{self._counters[rule]}",
                    args,
                )
            renamed[var] = by_sub[var]
        for var in substitution:
            renamed.pop(var, None)
        return renamed.compose(substitution)
