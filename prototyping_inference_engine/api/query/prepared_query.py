"""
Prepared query abstractions.
"""

from typing import Generic, Protocol, TypeVar, runtime_checkable

from prototyping_inference_engine.api.query.query import Query

Q_co = TypeVar("Q_co", bound=Query, covariant=True)
D_co = TypeVar("D_co", covariant=True)
A_co = TypeVar("A_co", covariant=True)
S_contra = TypeVar("S_contra", contravariant=True)


@runtime_checkable
class PreparedQuery(Protocol, Generic[Q_co, D_co, A_co, S_contra]):
    """
    Protocol for a prepared query.

    Implementations may provide estimate_bound, which should be a lightweight
    upper bound computation and must not perform expensive evaluation.
    """

    @property
    def query(self) -> Q_co: ...

    @property
    def data_source(self) -> D_co: ...

    def execute(self, assignation: S_contra) -> A_co: ...

    def estimate_bound(self, assignation: S_contra) -> int | None: ...
