from functools import cached_property
from typing import Optional

from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
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
        if isinstance(t1, Constant) and isinstance(t2, Constant):
            return 0
        elif isinstance(t1, Constant):
            return -1
        elif isinstance(t2, Constant):
            return 1
        return 0

    def is_valid(self, rule: Rule[ConjunctiveQuery, ConjunctiveQuery], context: ConjunctiveQuery = None) -> bool:
        for cls in self.classes:
            has_cst, has_head_exist, has_fr, has_ans_var = (False,)*4
            for t in cls:
                if isinstance(t, Constant):
                    if has_cst or has_head_exist:
                        return False
                    has_cst = True
                elif t in rule.existential_variables:
                    if has_head_exist or has_fr or has_cst or has_ans_var:
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

    def associated_substitution(self, context: Query = None) -> Optional[Substitution]:
        sub = Substitution()

        context_answer_variables, context_variables = set(), set()
        if context:
            context_answer_variables = context.answer_variables
            context_variables = context.variables

        for cls in self.classes:
            representative = None
            for t in cls:
                if representative is None:
                    representative = self.get_representative(t)

                if isinstance(t, Constant) and representative != t:
                    return None

                if (isinstance(representative, Variable)
                        and representative not in context_answer_variables
                        and t in context_variables):
                    representative = t
            for t in cls:
                if isinstance(t, Variable) and t != representative:
                    sub[t] = representative

        return sub

    @cached_property
    def is_admissible(self) -> bool:
        for cls in self.classes:
            representative = self.get_representative(next(iter(cls)))
            if isinstance(representative, Constant):
                for term in cls:
                    if term != representative and isinstance(term, Constant):
                        return False
        return True
