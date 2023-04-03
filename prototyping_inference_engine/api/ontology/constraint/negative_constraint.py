from typing import Optional

from prototyping_inference_engine.api.query.query import Query


class NegativeConstraint:
    def __init__(self, body: Query, label: Optional[str] = None):
        self._body = body.query_with_other_answer_variables(tuple())
        self._label = label

    @property
    def label(self) -> Optional[str]:
        return self._label

    @property
    def body(self) -> Query:
        return self._body

    def __repr__(self):
        return "Constraint: "+str(self)

    def __str__(self):
        return "{}{} -> \u22A5".format(
            "" if not self.label else "["+str(self.label)+"] ",
            str(self.body.str_without_answer_variables))
