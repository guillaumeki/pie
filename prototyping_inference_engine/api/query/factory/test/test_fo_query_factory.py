import unittest

from prototyping_inference_engine.api.query.factory.fo_query_factory import (
    FOQueryFactory,
)
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestFOQueryFactoryImport(unittest.TestCase):
    def setUp(self):
        self.session = ReasoningSession.create(auto_cleanup=False)

    def tearDown(self):
        self.session.close()

    def test_factory_instantiation(self):
        factory = FOQueryFactory(self.session)
        self.assertIsNotNone(factory)
