"""
MaterializedDataCollection for aggregating multiple materialized data sources.
"""
from typing import Dict, Iterator, List, Optional, Set, TYPE_CHECKING

from prototyping_inference_engine.api.data.materialized_data import MaterializedData
from prototyping_inference_engine.api.data.collection.readable_collection import (
    ReadableDataCollection,
)
from prototyping_inference_engine.api.data.collection.protocols import (
    Queryable,
    Materializable,
)

if TYPE_CHECKING:
    from prototyping_inference_engine.api.atom.atom import Atom
    from prototyping_inference_engine.api.atom.predicate import Predicate
    from prototyping_inference_engine.api.atom.term.constant import Constant
    from prototyping_inference_engine.api.atom.term.term import Term
    from prototyping_inference_engine.api.atom.term.variable import Variable


class MaterializedDataCollection(ReadableDataCollection, MaterializedData):
    """
    A collection that aggregates multiple materialized data sources.

    All sources must implement Materializable, enabling iteration, containment
    checks, and term inspection across the entire collection.

    This class implements MaterializedData, making it a drop-in replacement
    for in-memory FactBase instances in evaluators.

    Note: This implementation assumes single-threaded access. No synchronization
    is provided for concurrent access.
    """

    def __init__(
        self,
        sources: Dict["Predicate", Queryable],
        dynamic_sources: Optional[List[Queryable]] = None,
    ):
        """
        Create a collection from predicate-to-source mappings.

        Use MaterializedCollectionBuilder for a more convenient construction API.

        Args:
            sources: Mapping from predicates to their data sources.
                    All sources must implement Materializable.
            dynamic_sources: Sources that may add predicates dynamically.
                           Must also implement Materializable.

        Raises:
            TypeError: If any source does not implement Materializable
        """
        # Validate that all sources are Materializable
        all_sources = set(sources.values())
        if dynamic_sources:
            all_sources.update(dynamic_sources)

        for source in all_sources:
            if not isinstance(source, Materializable):
                raise TypeError(
                    f"All sources must implement Materializable, "
                    f"but {type(source).__name__} does not"
                )

        super().__init__(sources, dynamic_sources)
        self._cached_variables: Optional[Set["Variable"]] = None
        self._cached_constants: Optional[Set["Constant"]] = None
        self._cached_terms: Optional[Set["Term"]] = None

    def _get_materializable_sources(self) -> List[Materializable]:
        """Get all unique sources as Materializable instances."""
        return [s for s in self._all_sources if isinstance(s, Materializable)]

    def _invalidate_cache(self) -> None:
        """Invalidate cached term sets."""
        self._cached_variables = None
        self._cached_constants = None
        self._cached_terms = None

    def __iter__(self) -> Iterator["Atom"]:
        """Iterate over all atoms from all sources."""
        seen: Set["Atom"] = set()
        for source in self._get_materializable_sources():
            for atom in source:
                if atom not in seen:
                    seen.add(atom)
                    yield atom

    def __len__(self) -> int:
        """Return the total number of unique atoms across all sources."""
        return sum(1 for _ in self)

    def __contains__(self, atom: "Atom") -> bool:
        """Check if an atom is in any source."""
        source = self._get_source(atom.predicate)
        if source is not None and isinstance(source, Materializable):
            return atom in source
        return False

    @property
    def variables(self) -> Set["Variable"]:
        """All variables appearing in atoms across all sources."""
        if self._cached_variables is None:
            result: Set["Variable"] = set()
            for source in self._get_materializable_sources():
                result.update(source.variables)
            self._cached_variables = result
        return self._cached_variables

    @property
    def constants(self) -> Set["Constant"]:
        """All constants appearing in atoms across all sources."""
        if self._cached_constants is None:
            result: Set["Constant"] = set()
            for source in self._get_materializable_sources():
                result.update(source.constants)
            self._cached_constants = result
        return self._cached_constants

    @property
    def terms(self) -> Set["Term"]:
        """All terms appearing in atoms across all sources."""
        if self._cached_terms is None:
            result: Set["Term"] = set()
            for source in self._get_materializable_sources():
                result.update(source.terms)
            self._cached_terms = result
        return self._cached_terms

    def __repr__(self) -> str:
        predicates = list(self._sources.keys())
        if len(predicates) <= 3:
            pred_str = ", ".join(str(p) for p in predicates)
        else:
            pred_str = f"{len(predicates)} predicates"
        return f"MaterializedDataCollection({pred_str})"
