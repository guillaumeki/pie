from typing import Iterable, Optional, Type, TYPE_CHECKING

from prototyping_inference_engine.api.atom.atom import Atom

if TYPE_CHECKING:
    from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import FrozenInMemoryFactBase
    from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase


class FactBaseFactory:
    """Factory for creating FactBase instances (facilitates testing)."""

    _frozen_impl: Optional[Type["FrozenInMemoryFactBase"]] = None
    _mutable_impl: Optional[Type["MutableInMemoryFactBase"]] = None

    @classmethod
    def create_frozen(cls, atoms: Iterable[Atom] = None) -> "FrozenInMemoryFactBase":
        from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import FrozenInMemoryFactBase
        impl = cls._frozen_impl or FrozenInMemoryFactBase
        return impl(atoms)

    @classmethod
    def create_mutable(cls, atoms: Iterable[Atom] = None) -> "MutableInMemoryFactBase":
        from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import MutableInMemoryFactBase
        impl = cls._mutable_impl or MutableInMemoryFactBase
        return impl(atoms)

    @classmethod
    def configure(cls, frozen_impl: Type["FrozenInMemoryFactBase"] = None,
                  mutable_impl: Type["MutableInMemoryFactBase"] = None) -> None:
        cls._frozen_impl = frozen_impl
        cls._mutable_impl = mutable_impl

    @classmethod
    def reset(cls) -> None:
        cls._frozen_impl = None
        cls._mutable_impl = None
