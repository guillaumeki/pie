"""Rule body transformer using all free variables as answers."""

from __future__ import annotations

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.forward_chaining.chase.rule_applier.body_to_query_transformer.body_to_query_transformer import (
    BodyToQueryTransformer,
)


class AllTransformer(BodyToQueryTransformer):
    def transform(self, rule: Rule) -> FOQuery:
        return FOQuery(rule.body, sorted(rule.body.free_variables, key=str))
