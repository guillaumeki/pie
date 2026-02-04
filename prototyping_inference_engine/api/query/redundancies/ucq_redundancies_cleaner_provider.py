from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_union_conjunctive_queries import (
        RedundanciesCleanerUnionConjunctiveQueries,
    )


@runtime_checkable
class UCQRedundanciesCleanerProvider(Protocol):
    """Protocol for providing a RedundanciesCleanerUnionConjunctiveQueries."""

    def get_cleaner(self) -> "RedundanciesCleanerUnionConjunctiveQueries": ...


class DefaultUCQRedundanciesCleanerProvider:
    """Provides default RedundanciesCleanerUnionConjunctiveQueries."""

    def get_cleaner(self) -> "RedundanciesCleanerUnionConjunctiveQueries":
        from prototyping_inference_engine.api.query.redundancies.redundancies_cleaner_union_conjunctive_queries import (
            RedundanciesCleanerUnionConjunctiveQueries,
        )

        return RedundanciesCleanerUnionConjunctiveQueries.instance()
