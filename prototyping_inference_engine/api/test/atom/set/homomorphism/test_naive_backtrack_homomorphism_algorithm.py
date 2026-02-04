from unittest import TestCase

from prototyping_inference_engine.api.atom.set.homomorphism.backtrack.naive_backtrack_homomorphism_algorithm import NaiveBacktrackHomomorphismAlgorithm
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.substitution.substitution import Substitution
from prototyping_inference_engine.parser.dlgp.dlgp2_parser import Dlgp2Parser


class TestNaiveBacktrackHomomorphismAlgorithm(TestCase):
    data: tuple[dict[str, object], ...] = (
        {
            "from": "p(X,Y).",
            "to": "p(a,b).",
            "pre_sub": None,
            "homomorphisms": (Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("b")}),)
        },
        {
            "from": "p(X,Y).",
            "to": "p(a,a).",
            "pre_sub": None,
            "homomorphisms": (Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("a")}),)
        },
        {
            "from": "p(X,X).",
            "to": "p(a,b).",
            "pre_sub": None,
            "homomorphisms": tuple()
        },
        {
            "from": "p(X,X), p(X,Y).",
            "to": "p(a,b), p(a,a).",
            "pre_sub": None,
            "homomorphisms": (Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("b")}),
                              Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("a")}),)
        },
        {
            "from": "p(a,X), p(X,Y).",
            "to": "p(a,b), p(a,a).",
            "pre_sub": None,
            "homomorphisms": (Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("b")}),
                              Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("a")}),)
        },
        {
            "from": "p(a,X), q(X,Y).",
            "to": "q(a,b), p(a,a).",
            "pre_sub": None,
            "homomorphisms": (Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("b")}),)
        },
        {
            "from": "p(a,X), q(X,Y).",
            "to": "q(a,b), p(a,a),t(c,d).",
            "pre_sub": None,
            "homomorphisms": (Substitution({Variable("X"): Constant("a"), Variable("Y"): Constant("b")}),)
        },
        {
            "from": "p(a,X), t(X,Y).",
            "to": "q(a,b), p(a,a).",
            "pre_sub": None,
            "homomorphisms": ()
        },
        {
            "from": "p(a, a), p(Y, Z), p(X, Y), p(a, X), p(X, Z).",
            "to": "p(a,a).",
            "pre_sub": None,
            "homomorphisms": (Substitution({Variable("X"): Constant("a"),
                                            Variable("Y"): Constant("a"),
                                            Variable("Z"): Constant("a"), }),)
        },
        {
            "from": "p(a, a).",
            "to": "p(a, a), p(Y, Z), p(X, Y), p(a, X), p(X, Z).",
            "pre_sub": None,
            "homomorphisms": (Substitution({}),)
        },
        {
            "from": "p(U24, U14), p(U23, U13), p(U13, U24), r(U23), q(U14).",
            "to": "p(V, W), q(T), p(U, V), p(W, T), r(U).",
            "pre_sub": Substitution({}),
            "homomorphisms": (Substitution({Variable("U14"): Variable("T"),
                                            Variable("U24"): Variable("W"),
                                            Variable("U13"): Variable("V"),
                                            Variable("U23"): Variable("U")
                                            }),)
        },
        {
            "from": "p(V, W), q(T), p(U, V), p(W, T), r(U).",
            "to": "p(U24, U14), p(U23, U13), p(U13, U24), r(U23), q(U14).",
            "pre_sub": Substitution({}),
            "homomorphisms": (Substitution({Variable("T"): Variable("U14"),
                                            Variable("W"): Variable("U24"),
                                            Variable("V"): Variable("U13"),
                                            Variable("U"): Variable("U23")
                                            }),)
        },
    )

    def test_compute_homomorphisms(self):
        nbha = NaiveBacktrackHomomorphismAlgorithm()
        for d in self.data:
            from_ = Dlgp2Parser.instance().parse_atoms(d["from"])
            to = Dlgp2Parser.instance().parse_atoms(d["to"])

            homomorphisms = tuple(nbha.compute_homomorphisms(from_, to, d["pre_sub"]))
            # print(homomorphisms)

            self.assertTrue(all(h in homomorphisms for h in d["homomorphisms"]), str(d) + "\n" + str(homomorphisms))
            self.assertTrue(all(h in d["homomorphisms"] for h in homomorphisms), str(d) + "\n" + str(homomorphisms))

    def test_exist_homomorphisms(self):
        nbha = NaiveBacktrackHomomorphismAlgorithm()
        for d in self.data:
            from_ = Dlgp2Parser.instance().parse_atoms(d["from"])
            to = Dlgp2Parser.instance().parse_atoms(d["to"])

            # homomorphisms = tuple(nbha.compute_homomorphisms(from_, to, d["pre_sub"]))
            # print(homomorphisms)
            self.assertTrue((len(d["homomorphisms"]) > 0) == nbha.exist_homomorphism(from_, to, d["pre_sub"]))
