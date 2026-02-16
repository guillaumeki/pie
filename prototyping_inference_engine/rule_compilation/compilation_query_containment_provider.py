"""
Containment provider using rule compilation.
"""

from __future__ import annotations

from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import (
    ConjunctiveQueryContainment,
)
from prototyping_inference_engine.rule_compilation.api.rule_compilation import (
    RuleCompilation,
)
from prototyping_inference_engine.rule_compilation.compilation_cq_containment import (
    CompilationAwareCQContainment,
)


class CompilationAwareCQContainmentProvider:
    def __init__(self, compilation: RuleCompilation) -> None:
        self._compilation = compilation

    def get_containment(self) -> ConjunctiveQueryContainment:
        return CompilationAwareCQContainment(self._compilation)
