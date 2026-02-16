#
# References:
# - "A Sound and Complete Backward Chaining Algorithm for Existential Rules" —
#   Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo.
#   Link: https://ceur-ws.org/Vol-920/paper17.pdf
# - "Sound, Complete, and Minimal Query Rewriting for Existential Rules" —
#   Markus Konig, Michel Leclere, Marie-Laure Mugnier, Michael Thomazo.
#   Link: https://www.ijcai.org/Proceedings/13/Papers/292.pdf
#
# Summary:
# UCQ rewriting is the backward chaining technique for existential rules that
# repeatedly replaces query atoms using rule heads to produce a union of CQs.
#
# Properties used here:
# - Soundness/completeness of UCQ rewriting relative to the rule set.
# - Minimality when combined with redundancy elimination.
#
# Implementation notes:
# This abstract interface captures the UCQ rewriting contract implemented by
# concrete algorithms (e.g., breadth-first rewriting).

from abc import ABC, abstractmethod
from math import inf
from typing import Callable, Optional

from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.union_query import UnionQuery


class UcqRewritingAlgorithm(ABC):
    @abstractmethod
    def rewrite(
        self,
        ucq: UnionQuery[ConjunctiveQuery],
        rule_set: set[Rule],
        step_limit: float = inf,
        verbose: bool = False,
        printer: Optional[Callable[[UnionQuery[ConjunctiveQuery], int], None]] = None,
    ) -> UnionQuery[ConjunctiveQuery]:
        pass
