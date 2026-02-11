import tempfile
import unittest
from pathlib import Path

from prototyping_inference_engine.rdf.translator import RDFTranslationMode
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestImportResolution(unittest.TestCase):
    def test_imports_csv_and_rdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            csv_path = base / "facts.csv"
            csv_path.write_text("a,b\n", encoding="utf-8")

            rdf_path = base / "data.ttl"
            rdf_path.write_text(
                """
                @prefix ex: <http://example.org/> .
                ex:a ex:knows ex:b .
                """,
                encoding="utf-8",
            )

            dlgpe_path = base / "main.dlgpe"
            dlgpe_path.write_text(
                """
                @import <facts.csv>.
                @import <data.ttl>.

                @facts
                p(a).
                """,
                encoding="utf-8",
            )

            session = ReasoningSession.create(
                rdf_translation_mode=RDFTranslationMode.RAW
            )
            result = session.parse_file(dlgpe_path)

            predicates = {atom.predicate.name for atom in result.facts}
            self.assertIn("p", predicates)
            self.assertIn("facts", predicates)
            self.assertIn("triple", predicates)
