"""
Helper for filtering out virtually removed atoms from query results.
"""

from typing import Iterable, Iterator, cast

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.data.basic_query import BasicQuery


class DelAtomWrapper:
    """
    Utility for removing specific atoms from query results without mutating data sources.
    """

    def __init__(self, removed_atoms: Iterable[Atom]):
        self._removed_atoms = set(removed_atoms)

    @property
    def removed_atoms(self) -> set[Atom]:
        return set(self._removed_atoms)

    def is_removed(self, atom: Atom) -> bool:
        return atom in self._removed_atoms

    def filter_results(
        self, query: BasicQuery, results: Iterator[tuple[Term, ...]]
    ) -> Iterator[tuple[Term, ...]]:
        """
        Filter query results by excluding atoms marked as removed.
        """
        answer_positions = sorted(query.answer_variables.keys())
        if len(answer_positions) != query.predicate.arity - len(query.bound_positions):
            raise ValueError(
                "Cannot filter results when query does not define all positions."
            )

        for row in results:
            if len(row) != len(answer_positions):
                raise ValueError("Result row length does not match answer positions.")
            terms: list[Term | None] = [None] * query.predicate.arity
            for pos, term in query.bound_positions.items():
                terms[pos] = term
            for idx, pos in enumerate(answer_positions):
                terms[pos] = row[idx]
            if any(term is None for term in terms):
                raise ValueError("Query does not define all atom positions.")
            atom = Atom(query.predicate, *cast(list[Term], terms))
            if not self.is_removed(atom):
                yield row
