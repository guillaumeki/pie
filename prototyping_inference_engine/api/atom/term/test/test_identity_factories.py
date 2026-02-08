from unittest import TestCase

from prototyping_inference_engine.api.atom.term.factory.identity_term_factory import (
    IdentityVariableFactory,
    IdentityConstantFactory,
    IdentityLiteralFactory,
)
from prototyping_inference_engine.api.atom.term.factory.identity_predicate_factory import (
    IdentityPredicateFactory,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage


class TestIdentityFactories(TestCase):
    def test_identity_variable_factory_uniqueness(self):
        factory = IdentityVariableFactory(DictStorage())
        x1 = factory.create("X")
        x2 = factory.create("X")
        self.assertIs(x1, x2)

    def test_identity_constant_factory_uniqueness(self):
        factory = IdentityConstantFactory(DictStorage())
        c1 = factory.create("a")
        c2 = factory.create("a")
        self.assertIs(c1, c2)

    def test_identity_literal_factory_uniqueness(self):
        factory = IdentityLiteralFactory(DictStorage())
        l1 = factory.create("a")
        l2 = factory.create("a")
        self.assertIs(l1, l2)

    def test_identity_predicate_factory_uniqueness(self):
        factory = IdentityPredicateFactory(DictStorage())
        p1 = factory.create("p", 2)
        p2 = factory.create("p", 2)
        self.assertIs(p1, p2)

    def test_identity_factories_do_not_mix(self):
        factory1 = IdentityVariableFactory(DictStorage())
        factory2 = IdentityVariableFactory(DictStorage())
        x1 = factory1.create("X")
        x2 = factory2.create("X")
        self.assertIsNot(x1, x2)
