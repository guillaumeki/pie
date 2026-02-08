"""
Prepared FOQuery abstraction.
"""

from typing import Iterable, Protocol, runtime_checkable

from prototyping_inference_engine.api.data.readable_data import ReadableData
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.query.prepared_query import PreparedQuery
from prototyping_inference_engine.api.substitution.substitution import Substitution


@runtime_checkable
class PreparedFOQuery(
    PreparedQuery[FOQuery, ReadableData, Iterable[Substitution], Substitution],
    Protocol,
):
    """
    Prepared FOQuery that can be executed with a substitution.
    """

    pass


class PreparedFOQueryDefaults:
    """Optional mixin providing default behaviors for prepared FO queries."""

    def execute_empty(self) -> Iterable[Substitution]:
        return self.execute(Substitution())

    def is_evaluable_with(self, substitution: Substitution) -> bool:
        return True

    def mandatory_parameters(self) -> set:
        return set()
