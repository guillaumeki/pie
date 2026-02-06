import unittest

from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestDlgpeLiterals(unittest.TestCase):
    def test_dlgpe_literals_parse(self):
        text = """
        @facts
        p(1).
        p(1.50).
        p(true).
        p("chat").
        p("01"^^xsd:integer).
        """
        facts = list(DlgpeParser.instance().parse_atoms(text))
        terms = [atom.terms[0] for atom in facts]

        self.assertTrue(all(isinstance(t, Literal) for t in terms))

        values = [t.value for t in terms]
        self.assertIn(1, values)
        self.assertIn(1.5, values)
        self.assertIn(True, values)

        string_terms = [t for t in terms if t.datatype == "xsd:string"]
        self.assertEqual(len(string_terms), 1)
        self.assertEqual(string_terms[0].value, "chat")
        self.assertEqual(str(string_terms[0]), '"chat"')
