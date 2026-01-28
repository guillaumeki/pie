from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.set.homomorphism.homomorphism_algorithm import HomomorphismAlgorithm


@runtime_checkable
class HomomorphismAlgorithmProvider(Protocol):
    """Protocol for providing a HomomorphismAlgorithm."""

    def get_algorithm(self) -> "HomomorphismAlgorithm":
        ...


class DefaultHomomorphismAlgorithmProvider:
    """Provides NaiveBacktrackHomomorphismAlgorithm as the default."""

    def get_algorithm(self) -> "HomomorphismAlgorithm":
        from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.naive_backtrack_homomorphism_algorithm import \
            NaiveBacktrackHomomorphismAlgorithm
        return NaiveBacktrackHomomorphismAlgorithm.instance()
