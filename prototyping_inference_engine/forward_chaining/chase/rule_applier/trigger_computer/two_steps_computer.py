"""Two-steps trigger computer."""

from __future__ import annotations

from collections.abc import Collection, Iterable

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.substitution_key import (
    substitution_key,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.trigger_computer import (
    TriggerComputer,
)
from prototyping_inference_engine.query_evaluation.evaluator.fo_query.fo_query_evaluators import (
    GenericFOQueryEvaluator,
)


class TwoStepsComputer(TriggerComputer):
    def __init__(self, evaluator: GenericFOQueryEvaluator | None = None):
        self._evaluator = evaluator or GenericFOQueryEvaluator()
        self._chase: Chase | None = None

    def init(self, chase: Chase) -> None:
        self._chase = chase

    def compute(
        self,
        body: FOQuery,
        rules: Collection[Rule],
        chasable_data: ChasableData,
    ) -> Iterable[Substitution]:
        if self._chase is None:
            return self._evaluator.evaluate(body, chasable_data.get_all_readable_data())

        last_step_facts = self._chase.get_last_step_results().created_facts
        data = chasable_data.get_all_readable_data()

        if last_step_facts is None:
            return self._evaluator.evaluate(body, data)

        body_atoms = list(body.formula.atoms)
        if len(body_atoms) == 1:
            return self._evaluator.evaluate(body, last_step_facts)

        all_results: list[Substitution] = []
        seen: set[tuple[tuple[object, object], ...]] = set()

        for atom in body_atoms:
            atom_query = FOQuery(atom, sorted(atom.free_variables, key=str))
            for seed in self._evaluator.evaluate(atom_query, last_step_facts):
                for full in self._evaluator.evaluate(body, data, seed):
                    merged = _merge_compatible(seed, full)
                    if merged is None:
                        continue
                    norm = merged.normalize()
                    key = substitution_key(norm)
                    if key not in seen:
                        seen.add(key)
                        all_results.append(norm)

        return all_results


def _merge_compatible(left: Substitution, right: Substitution) -> Substitution | None:
    merged = Substitution(dict(left))
    for var in right:
        if var in merged and merged[var] != right[var]:
            return None
        merged[var] = right[var]
    return merged
