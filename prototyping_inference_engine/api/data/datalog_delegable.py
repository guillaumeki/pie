"""
Protocol for data sources that can delegate datalog rules and conjunctive queries.
"""

from typing import Iterable, Iterator, Protocol, runtime_checkable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.ontology.rule.rule import Rule
    from prototyping_inference_engine.api.query.fo_query import FOQuery
    from prototyping_inference_engine.api.substitution.substitution import Substitution


@runtime_checkable
class DatalogDelegable(Protocol):
    """
    Protocol for data sources that can directly apply datalog rules and evaluate
    conjunctive queries.
    """

    def delegate_rules(self, rules: Iterable["Rule"]) -> bool:
        """
        Apply a collection of datalog rules and return True if new facts are added.
        """

    def delegate_query(
        self, query: "FOQuery", count_answers_only: bool = False
    ) -> Iterator["Substitution"]:
        """
        Delegate query evaluation to the data source.
        """

    def delegate(
        self, query: "FOQuery", count_answers_only: bool = False
    ) -> Iterator["Substitution"]:
        """
        Default delegating hook for FOQuery evaluation.
        """
        return self.delegate_query(query, count_answers_only=count_answers_only)
