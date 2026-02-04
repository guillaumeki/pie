from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.backward_chaining.rewriting_operator.rewriting_operator import (
        RewritingOperator,
    )


@runtime_checkable
class RewritingOperatorProvider(Protocol):
    """Protocol for providing a RewritingOperator."""

    def get_operator(self) -> "RewritingOperator": ...


class DefaultRewritingOperatorProvider:
    """Provides WithoutAggregationRewritingOperator as the default."""

    def get_operator(self) -> "RewritingOperator":
        from prototyping_inference_engine.backward_chaining.rewriting_operator.without_aggregation_rewriting_operator import (
            WithoutAggregationRewritingOperator,
        )

        return WithoutAggregationRewritingOperator()
