import unittest

from prototyping_inference_engine.api.iri.iri import IRIRef
from prototyping_inference_engine.api.iri.manager import IRIManager, PrefixedIRIRef
from prototyping_inference_engine.api.iri.normalization import (
    RFCNormalizationScheme,
    StandardComposableNormalizer,
)


class TestIRIManager(unittest.TestCase):
    manager: IRIManager

    @classmethod
    def setUpClass(cls) -> None:
        cls.manager = IRIManager(
            None,
            StandardComposableNormalizer(
                RFCNormalizationScheme.SYNTAX,
                RFCNormalizationScheme.SCHEME,
            ),
            "foo",
        )
        cls.manager.set_prefix("ex1", "bar/")
        cls.manager.set_prefix_from_prefix("ex2", "ex1", "baz")
        cls.manager.set_prefix_from_prefix("ex1", "ex2", "bar/")
        cls.manager.set_base_from_prefix("ex1", "foo/")
        cls.manager.set_prefix("Ihis_Is_Far_Too_Long_To_Be_Useful", "http://test/")

    def test_manager_base(self) -> None:
        expected = "http://www.boreal.inria.fr/bar/bar/foo/"
        self.assertEqual(expected, self.manager.get_base())

    def test_manager_keys(self) -> None:
        expected = {
            "ex1": "http://www.boreal.inria.fr/bar/bar/",
            "ex2": "http://www.boreal.inria.fr/bar/baz",
        }
        for key, value in expected.items():
            self.assertEqual(value, IRIRef(self.manager.get_prefix(key)).recompose())

    def test_relativize_all(self) -> None:
        expected = {
            "http://www.boreal.inria.fr/bar/bar/foo/": PrefixedIRIRef(None, IRIRef("")),
            "http://www.boreal.inria.fr/bar/foo/": PrefixedIRIRef(
                "ex2", IRIRef("foo/")
            ),
            "has://Nothing/to/do/with/it": PrefixedIRIRef(
                None, IRIRef("has://nothing/to/do/with/it")
            ),
            "http://test/foo": PrefixedIRIRef(None, IRIRef("//test/foo")),
            "https://test/foo": PrefixedIRIRef(None, IRIRef("https://test/foo")),
        }

        for value, expected_prefixed in expected.items():
            result = self.manager.relativize_best(self.manager.create_iri(value))
            self.assertEqual(expected_prefixed, result)


if __name__ == "__main__":
    unittest.main()
