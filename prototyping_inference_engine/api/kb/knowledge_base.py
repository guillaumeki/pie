from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.kb.rule_base import RuleBase


class KnowledgeBase:
    """
    Knowledge base grouping a FactBase and a RuleBase.

    Provides a minimal facade so callers can pass around a single object.
    """

    def __init__(self, fact_base: FactBase, rule_base: RuleBase):
        self._fact_base = fact_base
        self._rule_base = rule_base

    @property
    def fact_base(self) -> FactBase:
        return self._fact_base

    @property
    def rule_base(self) -> RuleBase:
        return self._rule_base
