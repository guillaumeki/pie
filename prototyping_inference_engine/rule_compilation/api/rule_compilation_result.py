"""
Result container for rule compilation.
"""

from dataclasses import dataclass

from typing import TYPE_CHECKING

from prototyping_inference_engine.api.ontology.rule.rule import Rule

if TYPE_CHECKING:
    from prototyping_inference_engine.rule_compilation.api.rule_compilation import (
        RuleCompilation,
    )


@dataclass(frozen=True)
class RuleCompilationResult:
    compilation: "RuleCompilation"
    original_rule_set: list[Rule]
    compilable_rules: list[Rule]
    non_compilable_rules: list[Rule]
