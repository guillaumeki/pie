from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from prototyping_inference_engine.api.query.query import Query

Q = TypeVar("Q", bound=Query)


class QueryContainment(ABC, Generic[Q]):
    @abstractmethod
    def is_contained_in(self, q1: Q, q2: Q) -> bool:
        pass

    def is_equivalent_to(self, q1: Q, q2: Q) -> bool:
        return self.is_contained_in(q1, q2) and self.is_contained_in(q2, q1)
