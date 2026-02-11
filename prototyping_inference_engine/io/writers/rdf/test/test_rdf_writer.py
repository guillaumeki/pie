import tempfile
import unittest
from pathlib import Path

from rdflib import Graph  # type: ignore[import-not-found]

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.io.writers.rdf import RDFWriter
from prototyping_inference_engine.io.writers.rdf.rdf_writer import RDFWriterConfig
from prototyping_inference_engine.rdf.translator import RDFTranslationMode
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestRDFWriter(unittest.TestCase):
    def test_write_natural_full(self):
        session = ReasoningSession.create()
        predicate = Predicate("http://example.org/Person", 1)
        atom = Atom(predicate, Constant("http://example.org/alice"))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "out.ttl"
            writer = RDFWriter(
                session.term_factories,
                RDFWriterConfig(translation_mode=RDFTranslationMode.NATURAL_FULL),
            )
            writer.write_atoms(path, [atom])

            graph = Graph()
            graph.parse(path, format="turtle")
            self.assertEqual(len(graph), 1)
