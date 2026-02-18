"""Immediately add produced atoms to the writable target."""

from __future__ import annotations

from typing import cast

from prototyping_inference_engine.api.fact_base.protocols import Writable
from prototyping_inference_engine.api.formula.conjunction_formula import (
    ConjunctionFormula,
)
from prototyping_inference_engine.api.formula.formula import Formula
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.forward_chaining.chase.rule_applier.trigger_applier.facts_handler.facts_handler import (
    FactsHandler,
)


class DirectApplication(FactsHandler):
    def add(self, new_facts: Formula, read_write_data: FactBase) -> Formula | None:
        writable = cast(Writable, read_write_data)
        added_atoms = []
        for atom in new_facts.atoms:
            if atom in read_write_data:
                continue
            writable.add(atom)
            added_atoms.append(atom)
        if not added_atoms:
            return None
        formula: Formula = added_atoms[0]
        for atom in added_atoms[1:]:
            formula = ConjunctionFormula(formula, atom)
        return formula
