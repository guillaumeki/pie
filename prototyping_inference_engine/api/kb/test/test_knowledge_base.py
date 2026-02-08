from unittest import TestCase

from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.api.kb.knowledge_base import KnowledgeBase
from prototyping_inference_engine.api.kb.rule_base import RuleBase


class TestKnowledgeBase(TestCase):
    def test_knowledge_base_holds_fact_and_rule_base(self):
        fact_base = FrozenInMemoryFactBase()
        rule_base = RuleBase()
        kb = KnowledgeBase(fact_base, rule_base)
        self.assertIs(kb.fact_base, fact_base)
        self.assertIs(kb.rule_base, rule_base)
