import tempfile
import unittest
from pathlib import Path

from prototyping_inference_engine.io.parsers.rdf import RDFParser
from prototyping_inference_engine.io.parsers.rdf.rdf_parser import RDFParserConfig
from prototyping_inference_engine.rdf.translator import RDFTranslationMode
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestRDFParser(unittest.TestCase):
    def test_parse_natural_full(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.ttl"
            path.write_text(
                """
                @prefix ex: <http://example.org/> .
                @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
                ex:a rdf:type ex:Person .
                ex:a ex:knows "bob" .
                """,
                encoding="utf-8",
            )

            session = ReasoningSession.create()
            parser = RDFParser(
                path,
                session.term_factories,
                RDFParserConfig(translation_mode=RDFTranslationMode.NATURAL_FULL),
            )
            atoms = list(parser.parse_atoms())
            predicates = {atom.predicate.name for atom in atoms}

            self.assertIn("http://example.org/Person", predicates)
            self.assertIn("http://example.org/knows", predicates)

    def test_parse_raw(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.ttl"
            path.write_text(
                """
                @prefix ex: <http://example.org/> .
                ex:a ex:knows ex:b .
                """,
                encoding="utf-8",
            )

            session = ReasoningSession.create()
            parser = RDFParser(
                path,
                session.term_factories,
                RDFParserConfig(translation_mode=RDFTranslationMode.RAW),
            )
            atoms = list(parser.parse_atoms())

            self.assertEqual(len(atoms), 1)
            self.assertEqual(atoms[0].predicate.name, "triple")
            self.assertEqual(atoms[0].predicate.arity, 3)
