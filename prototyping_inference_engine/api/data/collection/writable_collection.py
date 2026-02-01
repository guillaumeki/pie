"""
WritableDataCollection for aggregating multiple writable data sources.
"""
from typing import Dict, Iterable, Iterator, List, Optional, TYPE_CHECKING

from prototyping_inference_engine.api.data.collection.materialized_collection import (
    MaterializedDataCollection,
)
from prototyping_inference_engine.api.data.collection.protocols import Queryable
from prototyping_inference_engine.api.fact_base.protocols import Writable

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.predicate import Predicate


class WritableDataCollection(MaterializedDataCollection):
    """
    A collection that aggregates multiple writable data sources.

    Supports adding atoms to the collection. Atoms are routed to the source
    responsible for their predicate, or to a default writable source if the
    predicate is not yet mapped.

    This class extends MaterializedDataCollection with write capabilities.

    Note: This implementation assumes single-threaded access. No synchronization
    is provided for concurrent access.
    """

    def __init__(
        self,
        sources: Dict["Predicate", Queryable],
        dynamic_sources: Optional[List[Queryable]] = None,
        default_writable: Optional[Writable] = None,
    ):
        """
        Create a writable collection from predicate-to-source mappings.

        Use WritableCollectionBuilder for a more convenient construction API.

        Args:
            sources: Mapping from predicates to their data sources.
                    All sources must implement Materializable.
            dynamic_sources: Sources that may add predicates dynamically.
            default_writable: Default destination for atoms with unmapped predicates.
                            If None, adding atoms with unmapped predicates raises KeyError.
        """
        super().__init__(sources, dynamic_sources)
        self._default_writable = default_writable
        if default_writable is not None and default_writable not in self._all_sources:
            self._all_sources.append(default_writable)

    def _get_writable_source(self, predicate: "Predicate") -> Optional[Writable]:
        """Get a writable source for a predicate."""
        source = self._get_source(predicate)
        if source is not None and isinstance(source, Writable):
            return source
        return self._default_writable

    def add(self, atom: "Atom") -> None:
        """
        Add an atom to the appropriate source.

        The atom is routed to the source responsible for its predicate.
        If no source owns the predicate, the default writable is used.
        If no default writable is configured, KeyError is raised.

        Args:
            atom: The atom to add

        Raises:
            KeyError: If no source owns the predicate and no default writable
            TypeError: If the owning source is not writable
        """
        predicate = atom.predicate
        source = self._get_source(predicate)

        if source is not None:
            if not isinstance(source, Writable):
                raise TypeError(
                    f"Source for predicate {predicate} does not support writing"
                )
            source.add(atom)
            # Register new predicate if needed
            if predicate not in self._sources:
                self._sources[predicate] = source
        elif self._default_writable is not None:
            self._default_writable.add(atom)
            # Register new predicate mapping to default writable
            self._sources[predicate] = self._default_writable
        else:
            raise KeyError(
                f"No writable source for predicate {predicate} "
                f"and no default writable configured"
            )

        self._invalidate_cache()

    def update(self, atoms: Iterable["Atom"]) -> None:
        """
        Add multiple atoms to their appropriate sources.

        Args:
            atoms: The atoms to add

        Raises:
            KeyError: If any atom's predicate has no writable source
            TypeError: If any owning source is not writable
        """
        for atom in atoms:
            self.add(atom)

    def __repr__(self) -> str:
        predicates = list(self._sources.keys())
        if len(predicates) <= 3:
            pred_str = ", ".join(str(p) for p in predicates)
        else:
            pred_str = f"{len(predicates)} predicates"
        writable_str = ", writable" if self._default_writable is not None else ""
        return f"WritableDataCollection({pred_str}{writable_str})"
