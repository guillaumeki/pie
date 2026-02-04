from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.set.core.core_algorithm import (
        CoreAlgorithm,
    )


@runtime_checkable
class CoreAlgorithmProvider(Protocol):
    """Protocol for providing a CoreAlgorithm."""

    def get_algorithm(self) -> "CoreAlgorithm": ...


class DefaultCoreAlgorithmProvider:
    """Provides NaiveCoreBySpecialization as the default."""

    def get_algorithm(self) -> "CoreAlgorithm":
        from prototyping_inference_engine.api.atom.set.core.naive_core_by_specialization import (
            NaiveCoreBySpecialization,
        )

        return NaiveCoreBySpecialization.instance()
