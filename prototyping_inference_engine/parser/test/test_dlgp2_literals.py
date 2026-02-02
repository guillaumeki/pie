import unittest

from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestDlgp2Literals(unittest.TestCase):
    def test_dlgp2_literals_parse(self):
        text = """
        p("chat"@fr).
        p("01"^^xsd:integer).
        p(1.5).
        p(false).
        """
        facts = list(Dlgp2Parser.instance().parse_atoms(text))
        terms = [atom.terms[0] for atom in facts]

        self.assertTrue(all(isinstance(t, Literal) for t in terms))
        lang_term = next(t for t in terms if t.lang == "fr")
        self.assertEqual(str(lang_term), "\"chat\"@fr")

        int_terms = [t for t in terms if t.datatype == "xsd:integer"]
        self.assertEqual(len(int_terms), 1)
        self.assertEqual(int_terms[0].value, 1)
        self.assertEqual(str(int_terms[0]), "1")

        decimal_terms = [t for t in terms if t.datatype == "xsd:decimal"]
        self.assertEqual(len(decimal_terms), 1)
        self.assertAlmostEqual(decimal_terms[0].value, 1.5)

        bool_terms = [t for t in terms if t.datatype == "xsd:boolean"]
        self.assertEqual(len(bool_terms), 1)
        self.assertEqual(str(bool_terms[0]), "false")
