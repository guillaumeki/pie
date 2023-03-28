from unittest import TestCase

from parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestDlgp2Parser(TestCase):
    def test_parse_atoms(self):
        atoms_str = "p(a), relatedTo(a,b), q(b). [f2] p(X), t(X,a,b), s(a,z), p(a)."
        #print(Dlgp2Parser.instance().parse_atoms(atoms_str))
