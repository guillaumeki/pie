"""Semi-naive trigger computer."""

from __future__ import annotations

from collections.abc import Collection, Iterable

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.data.queryable_data_del_atoms_wrapper import (
    QueryableDataDelAtomsWrapper,
)
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.forward_chaining.chase.chase import Chase
from prototyping_inference_engine.forward_chaining.chase.data.chasable_data import (
    ChasableData,
)
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_computer.naive_trigger_computer import (
    NaiveTriggerComputer,
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


class SemiNaiveComputer(TriggerComputer):
    def __init__(self, evaluator: GenericFOQueryEvaluator | None = None):
        self._evaluator = evaluator or GenericFOQueryEvaluator()
        self._fallback = NaiveTriggerComputer(self._evaluator)
        self._chase: Chase | None = None
        self._idb_predicates: set[Predicate] = set()

    def init(self, chase: Chase) -> None:
        self._chase = chase
        self._fallback.init(chase)
        self._idb_predicates = {
            atom.predicate
            for rule in chase.get_rule_base().rules
            for atom in rule.head.atoms
        }

    def compute(
        self,
        body: FOQuery,
        rules: Collection[Rule],
        chasable_data: ChasableData,
    ) -> Iterable[Substitution]:
        if self._chase is None:
            return self._fallback.compute(body, rules, chasable_data)

        last_step_facts = self._chase.get_last_step_results().created_facts
        if last_step_facts is None:
            return self._fallback.compute(body, rules, chasable_data)

        idb_atoms = [
            a for a in body.formula.atoms if a.predicate in self._idb_predicates
        ]
        edb_atoms = [
            a for a in body.formula.atoms if a.predicate not in self._idb_predicates
        ]
        if not idb_atoms:
            return self._fallback.compute(body, rules, chasable_data)

        data = chasable_data.get_all_readable_data()
        removed = QueryableDataDelAtomsWrapper(data, set(last_step_facts))
        seen: set[tuple[tuple[object, object], ...]] = set()
        results: list[Substitution] = []

        for i, anchor in enumerate(idb_atoms):
            left = idb_atoms[:i]
            right = idb_atoms[i + 1 :]

            seed_query = FOQuery(anchor, sorted(anchor.free_variables, key=str))
            seeds = list(self._evaluator.evaluate(seed_query, last_step_facts))
            partial: list[Substitution] = seeds
            if not partial:
                continue

            for atom in edb_atoms + left:
                partial = _join_with_atom(self._evaluator, partial, atom, data)
                if not partial:
                    break
            if not partial:
                continue

            for atom in right:
                partial = _join_with_atom(self._evaluator, partial, atom, removed)
                if not partial:
                    break

            for sub in partial:
                n = sub.normalize()
                key = substitution_key(n)
                if key not in seen:
                    seen.add(key)
                    results.append(n)

        return results


def _join_with_atom(
    evaluator: GenericFOQueryEvaluator,
    substitutions: list[Substitution],
    atom: Atom,
    data,
) -> list[Substitution]:
    out: list[Substitution] = []
    vars_for_atom = sorted(atom.free_variables, key=str)
    query = FOQuery(atom, vars_for_atom)

    for sub in substitutions:
        for ext in evaluator.evaluate(query, data, sub):
            merged = _merge_compatible(sub, ext)
            if merged is not None:
                out.append(merged)
    return out


def _merge_compatible(left: Substitution, right: Substitution) -> Substitution | None:
    merged = Substitution(dict(left))
    for var in right:
        if var in merged and merged[var] != right[var]:
            return None
        merged[var] = right[var]
    return merged
