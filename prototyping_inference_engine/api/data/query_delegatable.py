"""
QueryDelegatable protocol for data sources that can evaluate queries directly.
"""
from typing import Iterator, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.query.fo_query import FOQuery
    from prototyping_inference_engine.api.substitution.substitution import Substitution


class QueryDelegatable(Protocol):
    """
    Protocol for data sources that can evaluate FOQueries directly.

    This allows delegation of query evaluation to external systems
    (SQL databases, SPARQL endpoints, Datalog engines, etc.) that can
    process queries more efficiently than in-memory evaluation.
    """

    def is_delegatable(self, query: "FOQuery") -> bool:
        """
        Check if this data source can evaluate the query directly.

        Args:
            query: The query to check

        Returns:
            True if delegate() would produce results for this query
        """
        ...

    def delegate(
        self,
        query: "FOQuery",
        substitution: Optional["Substitution"] = None
    ) -> Iterator["Substitution"]:
        """
        Delegate query evaluation to the underlying data source.

        Args:
            query: The query to evaluate
            substitution: Optional initial substitution

        Returns:
            Iterator of substitutions representing query answers

        Raises:
            ValueError: If the query is not delegatable
        """
        ...
