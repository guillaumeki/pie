from functools import cached_property
from typing import Optional, cast

from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.query.query import Query
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.utils.partition import Partition


class TermPartition(Partition[Term]):
    def __init__(self, *args, **kwargs):
        if "comparator" not in kwargs:
            kwargs["comparator"] = TermPartition.default_comparator
        Partition.__init__(self, *args, **kwargs)

    @staticmethod
    def default_comparator(t1: Term, t2: Term) -> int:
        return t1.comparison_priority - t2.comparison_priority

    def is_valid(
        self,
        rule: Rule[ConjunctiveQuery, ConjunctiveQuery],
        context: Optional[ConjunctiveQuery] = None,
    ) -> bool:
        for cls in self.classes:
            has_ground, has_head_exist, has_fr, has_ans_var = (False,) * 4
            for t in cls:
                if t.is_ground:
                    if has_ground or has_head_exist:
                        return False
                    has_ground = True
                elif t in rule.existential_variables:
                    if has_head_exist or has_fr or has_ground or has_ans_var:
                        return False
                    has_head_exist = True
                elif t in rule.frontier:
                    if has_head_exist:
                        return False
                    has_fr = True
                elif context and t in context.answer_variables:
                    if has_head_exist:
                        return False
                    has_ans_var = True
        return True

    def associated_substitution(
        self, context: Optional[Query] = None
    ) -> Optional[Substitution]:
        sub = Substitution()

        context_answer_variables: set["Variable"] = set()
        context_variables: set["Variable"] = set()
        if context:
            context_answer_variables = set(context.answer_variables)
            context_variables = context.variables

        for cls in self.classes:
            representative: Optional[Term] = None
            for t in cls:
                if representative is None:
                    representative = self.get_representative(t)

                if t.is_ground and representative != t:
                    return None

                if (
                    not representative.is_ground
                    and representative not in context_answer_variables
                    and t in context_variables
                ):
                    representative = t
            for t in cls:
                if representative is None:
                    continue
                if not t.is_ground and t != representative:
                    from prototyping_inference_engine.api.atom.term.variable import (
                        Variable,
                    )

                    if isinstance(t, Variable):
                        sub[t] = cast(Term, representative)

        return sub

    @cached_property
    def is_admissible(self) -> bool:
        for cls in self.classes:
            representative = self.get_representative(next(iter(cls)))
            if representative.is_ground:
                for term in cls:
                    if term != representative and term.is_ground:
                        return False
        return True
