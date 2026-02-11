import tempfile
import unittest
from pathlib import Path

from prototyping_inference_engine.session.reasoning_session import ReasoningSession
from prototyping_inference_engine.io.parsers.csv import RLSCSVsParser


class TestRLSCSVParser(unittest.TestCase):
    def test_parse_rls_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            csv_path = base / "facts.csv"
            csv_path.write_text("a,b\nc,d\n", encoding="utf-8")

            rls_path = base / "config.rls"
            rls_path.write_text(
                '@source rel[2]: load-csv("facts.csv") .\n', encoding="utf-8"
            )

            session = ReasoningSession.create()
            parser = RLSCSVsParser(rls_path, session.term_factories)
            atoms = list(parser.parse_atoms())

            self.assertEqual(len(atoms), 2)
            self.assertEqual(atoms[0].predicate.name, "rel")
            self.assertEqual(atoms[0].predicate.arity, 2)
            self.assertEqual(atoms[0].terms[0].identifier, "a")
            self.assertEqual(atoms[0].terms[1].identifier, "b")
