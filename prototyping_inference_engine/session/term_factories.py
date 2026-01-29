"""
TermFactories registry for extensible term factory management.

This module provides a registry pattern for term factories,
enabling OCP-compliant extension with new term types.
"""
from typing import TypeVar, Generic, Any, Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.term.term import Term

T = TypeVar('T', bound='Term')


class TermFactories:
    """
    Extensible registry for term factories.

    Allows registering factories for different term types without
    modifying the ReasoningSession class (OCP compliance).

    Example usage:
        factories = TermFactories()
        factories.register(Variable, VariableFactory(storage))
        factories.register(Constant, ConstantFactory(storage))

        # Later, add new term type without modifying existing code
        factories.register(FunctionTerm, FunctionTermFactory(storage))

        # Retrieve and use
        var_factory = factories.get(Variable)
        x = var_factory.create("X")
    """

    def __init__(self) -> None:
        self._factories: dict[type, Any] = {}

    def register(self, term_type: type, factory: Any) -> None:
        """
        Register a factory for a term type.

        Args:
            term_type: The type of term (e.g., Variable, Constant)
            factory: The factory instance for creating terms of this type
        """
        self._factories[term_type] = factory

    def get(self, term_type: type) -> Any:
        """
        Get the factory for a term type.

        Args:
            term_type: The type of term to get the factory for

        Returns:
            The factory instance, or None if not registered

        Raises:
            KeyError: If no factory is registered for the term type
        """
        if term_type not in self._factories:
            raise KeyError(f"No factory registered for term type: {term_type.__name__}")
        return self._factories[term_type]

    def has(self, term_type: type) -> bool:
        """
        Check if a factory is registered for a term type.

        Args:
            term_type: The type of term to check

        Returns:
            True if a factory is registered
        """
        return term_type in self._factories

    def __contains__(self, term_type: type) -> bool:
        """Check if a factory is registered for a term type."""
        return self.has(term_type)

    def __len__(self) -> int:
        """Return the number of registered factories."""
        return len(self._factories)

    def __iter__(self) -> Iterator[type]:
        """Iterate over registered term types."""
        return iter(self._factories)

    def registered_types(self) -> set[type]:
        """
        Return all registered term types.

        Returns:
            A set of all term types with registered factories
        """
        return set(self._factories.keys())

    def clear(self) -> None:
        """Remove all registered factories."""
        self._factories.clear()
