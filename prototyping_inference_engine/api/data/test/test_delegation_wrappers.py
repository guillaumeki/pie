from unittest import TestCase

from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.queryable_data_del_atoms_wrapper import (
    QueryableDataDelAtomsWrapper,
)
from prototyping_inference_engine.api.fact_base.frozen_in_memory_fact_base import (
    FrozenInMemoryFactBase,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestQueryableDataDelAtomsWrapper(TestCase):
    def setUp(self):
        self.parser = DlgpeParser.instance()

    def test_filters_removed_atoms(self):
        atoms = list(self.parser.parse_atoms("p(a). p(b)."))
        fact_base = FrozenInMemoryFactBase(atoms)
        removed = {atoms[1]}
        wrapper = QueryableDataDelAtomsWrapper(fact_base, removed)

        query_atom = next(iter(self.parser.parse_atoms("p(X).")))
        query = BasicQuery.from_atom(query_atom)
        results = list(wrapper.evaluate(query))

        self.assertEqual(results, [(atoms[0].terms[0],)])
