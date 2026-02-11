import tempfile
import unittest
from pathlib import Path

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.io.writers.csv import CSVWriter


class TestCSVWriter(unittest.TestCase):
    def test_write_atoms(self):
        predicate = Predicate("p", 2)
        atoms = [Atom(predicate, Constant("a"), Constant("b"))]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "out.csv"
            writer = CSVWriter()
            writer.write_atoms(path, atoms)

            contents = path.read_text(encoding="utf-8").strip()
            self.assertEqual(contents, "a,b")
