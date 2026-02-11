import tempfile
import unittest
from pathlib import Path

from prototyping_inference_engine.session.reasoning_session import ReasoningSession
from prototyping_inference_engine.io.parsers.csv import CSVParser, CSVParserConfig


class TestCSVParser(unittest.TestCase):
    def test_parse_atoms_from_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "people.csv"
            path.write_text("alice,bob\ncarol,dave\n", encoding="utf-8")

            session = ReasoningSession.create()
            parser = CSVParser(path, session.term_factories)
            atoms = list(parser.parse_atoms())

            self.assertEqual(len(atoms), 2)
            self.assertEqual(atoms[0].predicate.name, "people")
            self.assertEqual(atoms[0].predicate.arity, 2)
            self.assertEqual(atoms[0].terms[0].identifier, "alice")
            self.assertEqual(atoms[0].terms[1].identifier, "bob")

    def test_parse_with_custom_predicate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.csv"
            path.write_text("x,y\n", encoding="utf-8")

            session = ReasoningSession.create()
            config = CSVParserConfig(prefix="ex:")
            parser = CSVParser(
                path,
                session.term_factories,
                predicate_name="ex:pair",
                predicate_arity=2,
                config=config,
            )
            atoms = list(parser.parse_atoms())

            self.assertEqual(len(atoms), 1)
            self.assertEqual(atoms[0].predicate.name, "ex:pair")
            self.assertEqual(atoms[0].predicate.arity, 2)

    def test_parse_with_quoted_fields(self):
        lorem = (
            "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
            "tempor incididunt ut labore et dolore magna aliqua."
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.csv"
            path.write_text(f"d,{lorem!r}\n".replace("'", '"'), encoding="utf-8")

            session = ReasoningSession.create()
            parser = CSVParser(path, session.term_factories)
            atoms = list(parser.parse_atoms())

            self.assertEqual(len(atoms), 1)
            self.assertEqual(atoms[0].terms[0].identifier, "d")
            self.assertEqual(atoms[0].terms[1].identifier, lorem)
