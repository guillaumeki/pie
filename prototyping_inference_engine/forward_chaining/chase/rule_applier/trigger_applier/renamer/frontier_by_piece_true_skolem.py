"""Frontier-by-piece true skolem renamer using logical function terms."""

from __future__ import annotations

from collections import defaultdict

from prototyping_inference_engine.api.atom.term.logical_function_term import (
    LogicalFunctionalTerm,
)
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.formula.universal_formula import UniversalFormula
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.formula_utils import (
    split_disjunction_formulas,
    split_into_single_piece_heads,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.substitution_key import (
    substitution_key,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.renamer.trigger_renamer import (
    TriggerRenamer,
)


class FrontierByPieceTrueSkolem(TriggerRenamer):
    def __init__(self) -> None:
        self._names: dict[
            Rule, dict[tuple[tuple[object, object], ...], dict[Variable, Term]]
        ] = defaultdict(dict)
        self._split_rules: dict[Rule, tuple[Rule, ...]] = {}
        self._counters: dict[Rule, int] = defaultdict(int)

    def rename_existentials(
        self, rule: Rule, substitution: Substitution
    ) -> Substitution:
        renamed = Substitution()
        for split_rule in self._split_rule(rule):
            frontier = Substitution(
                {
                    v: substitution.apply(v)
                    for v in split_rule.frontier
                    if substitution.apply(v) != v
                }
            )
            by_sub = self._names[rule].setdefault(substitution_key(frontier), {})
            for var in split_rule.existential_variables:
                if var not in by_sub:
                    self._counters[rule] += 1
                    args = tuple(frontier.values())
                    by_sub[var] = LogicalFunctionalTerm(
                        f"sk_frontier_piece_{rule.label or 'anon'}_{self._counters[rule]}",
                        args,
                    )
                renamed[var] = by_sub[var]

        for var in substitution:
            renamed.pop(var, None)
        return renamed.compose(substitution)

    def _split_rule(self, rule: Rule) -> tuple[Rule, ...]:
        if rule in self._split_rules:
            return self._split_rules[rule]

        pieces: list[Rule] = []
        for disjunct in split_disjunction_formulas(rule.head):
            for piece in split_into_single_piece_heads(disjunct):
                body = rule.body
                missing = body.free_variables - piece.free_variables
                for var in sorted(missing, key=str):
                    body = UniversalFormula(var, body)
                pieces.append(Rule(body, piece, rule.label))

        result = tuple(pieces) if pieces else (rule,)
        self._split_rules[rule] = result
        return result
