import unittest

from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestDlgpeIriResolution(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = DlgpeParser.instance()

    def test_resolves_base_and_prefix(self):
        text = """
            @base <http://example.org/base/>.
            @prefix ex: <http://example.org/ns/>.
            <rel>(ex:obj).
        """
        result = self.parser.parse(text)
        atom = result["facts"][0]
        self.assertEqual(atom.predicate.name, "http://example.org/base/rel")
        self.assertEqual(atom.terms[0].identifier, "http://example.org/ns/obj")

    def test_resolves_prefix_iri_against_base(self):
        text = """
            @base <http://example.org/base/>.
            @prefix ex: <relative/ns/>.
            ex:pred(a).
        """
        result = self.parser.parse(text)
        atom = result["facts"][0]
        self.assertEqual(
            atom.predicate.name, "http://example.org/base/relative/ns/pred"
        )
