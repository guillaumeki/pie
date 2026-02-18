"""Collect produced atoms without mutating target immediately."""

from __future__ import annotations

from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.facts_handler.facts_handler import (
    FactsHandler,
)


class DelegatedApplication(FactsHandler):
    def add(self, new_facts: Formula, read_write_data: FactBase) -> Formula | None:
        atoms_to_keep = [
            atom for atom in new_facts.atoms if atom not in read_write_data
        ]
        if not atoms_to_keep:
            return None
        formula: Formula = atoms_to_keep[0]
        for atom in atoms_to_keep[1:]:
            formula = ConjunctionFormula(formula, atom)
        return formula
