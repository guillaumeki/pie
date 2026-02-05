from unittest import TestCase

from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestDlgp2IriResolution(TestCase):
    def setUp(self) -> None:
        self.parser = Dlgp2Parser.instance()

    def test_resolves_base_and_prefix(self):
        text = "@base <http://example.org/base/> @prefix ex: <http://example.org/ns/> ex:pred(<rel>)."
        atoms = self.parser.parse_atoms(text)
        atom = list(atoms)[0]
        self.assertEqual(atom.predicate.name, "http://example.org/ns/pred")
        self.assertEqual(atom.terms[0].identifier, "http://example.org/base/rel")

        parsed = self.parser.parse(text)
        header = parsed.get("header", {})
        self.assertEqual(header.get("base"), "http://example.org/base/")
        self.assertEqual(header.get("prefixes", {}).get("ex"), "http://example.org/ns/")

    def test_resolves_prefix_iri_against_base(self):
        text = "@base <http://example.org/base/> @prefix ex: <relative/ns/> ex:pred(a)."
        atoms = self.parser.parse_atoms(text)
        atom = list(atoms)[0]
        self.assertEqual(
            atom.predicate.name,
            "http://example.org/base/relative/ns/pred",
        )
