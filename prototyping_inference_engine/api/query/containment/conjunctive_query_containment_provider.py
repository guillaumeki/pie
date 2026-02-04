from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import (
        ConjunctiveQueryContainment,
    )


@runtime_checkable
class ConjunctiveQueryContainmentProvider(Protocol):
    """Protocol for providing a ConjunctiveQueryContainment."""

    def get_containment(self) -> "ConjunctiveQueryContainment": ...


class DefaultCQContainmentProvider:
    """Provides HomomorphismBasedCQContainment as the default."""

    def get_containment(self) -> "ConjunctiveQueryContainment":
        from prototyping_inference_engine.api.query.containment.conjunctive_query_containment import (
            HomomorphismBasedCQContainment,
        )

        return HomomorphismBasedCQContainment.instance()
