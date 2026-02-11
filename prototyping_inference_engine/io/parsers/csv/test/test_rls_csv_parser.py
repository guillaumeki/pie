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

    def test_parse_multiple_sources(self):
        long_text = (
            "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
            "tempor incididunt ut labore et dolore magna aliqua."
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "csv1.csv").write_text(
                "a,b\na,c\na,d\nb,b\na,b\n", encoding="utf-8"
            )
            (base / "csv2.csv").write_text(
                f'b,"{long_text}"\nc,"{long_text}"\n', encoding="utf-8"
            )
            (base / "csv3.csv").write_text(
                f'd,e,"{long_text}"\nd,e,"Not {long_text}"\n', encoding="utf-8"
            )

            rls_path = base / "config.rls"
            rls_path.write_text(
                '@source p_csv[2]: load-csv("csv1.csv") .\n'
                '@source q_csv[2]: load-csv("csv2.csv") .\n'
                '@source r_csv[3]: load-csv("csv3.csv") .\n',
                encoding="utf-8",
            )

            session = ReasoningSession.create()
            parser = RLSCSVsParser(rls_path, session.term_factories)
            atoms = list(parser.parse_atoms())

            predicate_names = {atom.predicate.name for atom in atoms}
            self.assertEqual(predicate_names, {"p_csv", "q_csv", "r_csv"})
            self.assertEqual(len(atoms), 9)
