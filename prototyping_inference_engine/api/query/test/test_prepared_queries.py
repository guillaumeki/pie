from unittest import TestCase

from prototyping_inference_engine.api.query.prepared_query import PreparedQuery
from prototyping_inference_engine.api.query.prepared_fo_query import PreparedFOQuery
from prototyping_inference_engine.api.query.fo_query import FOQuery
from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.api.data.readable_data import ReadableData


class _PreparedQueryImpl:
    def __init__(self, query, data_source):
        self._query = query
        self._data_source = data_source

    @property
    def query(self):
        return self._query

    @property
    def data_source(self):
        return self._data_source

    def execute(self, assignation):
        return assignation

    def estimate_bound(self, assignation):
        return None


class _PreparedFOQueryImpl:
    def __init__(self, query, data_source):
        self._query = query
        self._data_source = data_source

    @property
    def query(self):
        return self._query

    @property
    def data_source(self):
        return self._data_source

    def execute(self, assignation: Substitution):
        yield assignation

    def estimate_bound(self, assignation: Substitution):
        return None

    def is_evaluable_with(self, substitution: Substitution) -> bool:
        return True

    def mandatory_parameters(self):
        return set()


class TestPreparedQueries(TestCase):
    def test_prepared_query_protocol(self):
        query = FOQuery(Atom(Predicate("p", 0)), [])
        prepared = _PreparedQueryImpl(query, object())
        self.assertIsInstance(prepared, PreparedQuery)

    def test_prepared_fo_query_protocol(self):
        class _Readable(ReadableData):
            def get_predicates(self):
                return iter(())

            def has_predicate(self, predicate):
                return False

            def get_atomic_pattern(self, predicate):
                raise NotImplementedError

            def evaluate(self, query):
                return iter(())

        query = FOQuery(Atom(Predicate("p", 0)), [])
        prepared = _PreparedFOQueryImpl(query, _Readable())
        self.assertIsInstance(prepared, PreparedFOQuery)
