from unittest import TestCase

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate, SpecialPredicate
from prototyping_inference_engine.api.atom.set.frozen_atom_set import FrozenAtomSet
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.term_partition import TermPartition
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.unifier.piece_unifier import (
    PieceUnifier,
)
from prototyping_inference_engine.unifier import (
    PieceUnifierAlgorithm,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser
from prototyping_inference_engine.io.parsers.dlgpe.conversions import (
    try_convert_fo_query,
)


def _parse_cq(text: str) -> ConjunctiveQuery:
    query = next(iter(DlgpeParser.instance().parse_queries(text)))
    converted = try_convert_fo_query(query)
    if not isinstance(converted, ConjunctiveQuery):
        raise AssertionError("Expected conjunctive query conversion to succeed.")
    return converted


def _build_cq_with_equality() -> ConjunctiveQuery:
    r = Predicate("r", 1)
    eq = SpecialPredicate.EQUALITY.value
    u = Variable("U")
    a = Constant("a")
    atoms = FrozenAtomSet([Atom(r, u), Atom(eq, u, a)])
    return ConjunctiveQuery(atoms, [])


class TestPieceUnifierAlgorithm(TestCase):
    data = (
        {
            "rule": "r(X,Y), q(Y) :- p(X).",
            "query": "?() :- r(U,V), q(V), r(U,U).",
            "piece_unifiers": {
                PieceUnifier(
                    rule=next(
                        iter(
                            DlgpeParser.instance().parse_rules("r(X,Y), q(Y) :- p(X).")
                        )
                    ),
                    query=_parse_cq("?() :- r(U,V), q(V), r(U,U)."),
                    unified_query_part=FrozenAtomSet(
                        DlgpeParser.instance().parse_atoms("r(U, V), q(V).")
                    ),
                    partition=TermPartition(
                        [{Variable("U"), Variable("X")}, {Variable("V"), Variable("Y")}]
                    ),
                )
            },
        },
        {
            "rule": "t(Y) :- r(X), p(X,Y).",
            "query": "?() :- t(U).",
            "piece_unifiers": {
                PieceUnifier(
                    rule=next(
                        iter(
                            DlgpeParser.instance().parse_rules("t(Y) :- r(X), p(X,Y).")
                        )
                    ),
                    query=_parse_cq("?() :- t(U)."),
                    unified_query_part=FrozenAtomSet(
                        DlgpeParser.instance().parse_atoms("t(U).")
                    ),
                    partition=TermPartition([{Variable("U"), Variable("Y")}]),
                )
            },
        },
        {
            "rule": "p(X,Y) :- q(X).",
            "query": "?() :- p(U,V), p(W,V), p(W,T), r(U,W).",
            "piece_unifiers": {
                PieceUnifier(
                    rule=next(
                        iter(DlgpeParser.instance().parse_rules("p(X,Y) :- q(X)."))
                    ),
                    query=_parse_cq("?() :- p(U,V), p(W,V), p(W,T), r(U,W)."),
                    unified_query_part=FrozenAtomSet(
                        DlgpeParser.instance().parse_atoms("p(U,V),p(W,V).")
                    ),
                    partition=TermPartition(
                        [
                            {Variable("X"), Variable("U"), Variable("W")},
                            {Variable("Y"), Variable("V")},
                        ]
                    ),
                ),
                PieceUnifier(
                    rule=next(
                        iter(DlgpeParser.instance().parse_rules("p(X,Y) :- q(X)."))
                    ),
                    query=_parse_cq("?() :- p(U,V), p(W,V), p(W,T), r(U,W)."),
                    unified_query_part=FrozenAtomSet(
                        DlgpeParser.instance().parse_atoms("p(W,T).")
                    ),
                    partition=TermPartition(
                        [{Variable("X"), Variable("W")}, {Variable("Y"), Variable("T")}]
                    ),
                ),
            },
        },
        {
            "rule": "p(X,Y) :- q(X,Y).",
            "query": "?() :- p(U,V), p(W,V), r(W,U).",
            "piece_unifiers": {
                PieceUnifier(
                    rule=next(
                        iter(DlgpeParser.instance().parse_rules("p(X,Y) :- q(X,Y)."))
                    ),
                    query=_parse_cq("?() :- p(U,V), p(W,V), r(W,U)."),
                    unified_query_part=FrozenAtomSet(
                        DlgpeParser.instance().parse_atoms("p(U,V).")
                    ),
                    partition=TermPartition(
                        [{Variable("X"), Variable("U")}, {Variable("Y"), Variable("V")}]
                    ),
                ),
                PieceUnifier(
                    rule=next(
                        iter(DlgpeParser.instance().parse_rules("p(X,Y) :- q(X,Y)."))
                    ),
                    query=_parse_cq("?() :- p(U,V), p(W,V), r(W,U)."),
                    unified_query_part=FrozenAtomSet(
                        DlgpeParser.instance().parse_atoms("p(W,V).")
                    ),
                    partition=TermPartition(
                        [{Variable("X"), Variable("W")}, {Variable("Y"), Variable("V")}]
                    ),
                ),
            },
        },
        {
            "rule": "p(X,Z) :- q(X,Y).",
            "query": "?() :- p(U,V), p(W,V), r(W,U).",
            "piece_unifiers": {
                PieceUnifier(
                    rule=next(
                        iter(DlgpeParser.instance().parse_rules("p(X,Z) :- q(X,Y)."))
                    ),
                    query=_parse_cq("?() :- p(U,V), p(W,V), r(W,U)."),
                    unified_query_part=FrozenAtomSet(
                        DlgpeParser.instance().parse_atoms("p(U,V),p(W,V).")
                    ),
                    partition=TermPartition(
                        [
                            {Variable("X"), Variable("U"), Variable("W")},
                            {Variable("Z"), Variable("V")},
                        ]
                    ),
                )
            },
        },
        {
            "rule": "q(X,Y) :- s(X).",
            "query": "?() :- q(V,U).",
            "piece_unifiers": {
                PieceUnifier(
                    rule=next(
                        iter(DlgpeParser.instance().parse_rules("q(X,Y) :- s(X)."))
                    ),
                    query=_parse_cq("?() :- q(V,U)."),
                    unified_query_part=FrozenAtomSet(
                        DlgpeParser.instance().parse_atoms("q(V,U).")
                    ),
                    partition=TermPartition(
                        [{Variable("X"), Variable("V")}, {Variable("Y"), Variable("U")}]
                    ),
                )
            },
        },
        {
            "rule": "q(X,Y) :- s(X).",
            "query": "?(U) :- q(V,U).",
            "piece_unifiers": set(),
        },
    )

    def test_compute_most_general_piece_unifiers(self):
        for d in self.data:
            rule = next(iter(DlgpeParser.instance().parse_rules(d["rule"])))
            query = _parse_cq(d["query"])
            self.assertEqual(
                set(
                    PieceUnifierAlgorithm.compute_most_general_mono_piece_unifiers(
                        query, rule
                    )
                ),
                d["piece_unifiers"],
            )

    def test_equality_partition_applied(self):
        rule = next(iter(DlgpeParser.instance().parse_rules("r(X) :- p(X).")))
        query = _build_cq_with_equality()

        unifiers = PieceUnifierAlgorithm.compute_most_general_mono_piece_unifiers(
            query, rule
        )
        self.assertEqual(len(unifiers), 1)
        partition = unifiers[0].partition
        self.assertEqual(
            partition.get_class(Variable("X")),
            {Variable("X"), Variable("U"), Constant("a")},
        )

    def test_equality_inconsistent_constants(self):
        r = Predicate("r", 1)
        eq = SpecialPredicate.EQUALITY.value
        u = Variable("U")
        a = Constant("a")
        b = Constant("b")
        atoms = FrozenAtomSet([Atom(r, u), Atom(eq, u, a), Atom(eq, u, b)])
        query = ConjunctiveQuery(atoms, [])
        rule = next(iter(DlgpeParser.instance().parse_rules("r(X) :- p(X).")))

        unifiers = PieceUnifierAlgorithm.compute_most_general_mono_piece_unifiers(
            query, rule
        )
        self.assertEqual(unifiers, [])

    def test_integraal_unifier_partitions(self):
        cases = (
            {
                "rule": "p(X,Y) :- q(X,Y).",
                "query": "?() :- p(U,V), p(W,V), r(W,U).",
                "expected": {
                    TermPartition(
                        [{Variable("X"), Variable("U")}, {Variable("Y"), Variable("V")}]
                    ),
                    TermPartition(
                        [{Variable("X"), Variable("W")}, {Variable("Y"), Variable("V")}]
                    ),
                },
            },
            {
                "rule": "p(X,Z) :- q(X,Y).",
                "query": "?() :- p(U,V), p(W,V), r(W,U).",
                "expected": {
                    TermPartition(
                        [
                            {Variable("X"), Variable("U"), Variable("W")},
                            {Variable("Z"), Variable("V")},
                        ]
                    )
                },
            },
            {
                "rule": "q(X,Y) :- s(X).",
                "query": "?(U) :- q(V,U).",
                "expected": set(),
            },
        )

        for case in cases:
            rule = next(iter(DlgpeParser.instance().parse_rules(case["rule"])))
            query = _parse_cq(case["query"])
            unifiers = PieceUnifierAlgorithm.compute_most_general_mono_piece_unifiers(
                query, rule
            )
            partitions = {u.partition for u in unifiers}
            self.assertEqual(partitions, case["expected"])

    """def test__compute_separating_sticky_variables(self):
        pass

    def test__exists_separating_sticky_variables(self):
        pass

    def test__compute_atomic_pre_unifiers(self):
        pass

    def test__compute_var_to_query_atoms(self):
        pass

    def test__compute_atom_to_atomic_pre_unifiers(self):
        pass

    def test__extend_atomic_pre_unifiers(self):
        pass

    def test__compute_local_extension(self):
        pass"""
