from typing import Iterable, Callable

from lark import Lark

from prototyping_inference_engine.api.atom.set.atom_set import AtomSet
from prototyping_inference_engine.api.query.conjunctive_query import ConjunctiveQuery
from prototyping_inference_engine.api.atom.set.mutable_atom_set import MutableAtomSet
from prototyping_inference_engine.api.ontology.constraint.negative_constraint import NegativeConstraint
from prototyping_inference_engine.api.ontology.rule.rule import Rule
from prototyping_inference_engine.api.query.union_conjunctive_queries import UnionConjunctiveQueries
from prototyping_inference_engine.parser.dlgp.dlgp2_transformer import Dlgp2Transformer


class Dlgp2Parser:
    _instance = None

    def __init__(self):
        self._parser = Lark.open("dlgp2.lark", rel_to=__file__, parser="lalr", transformer=Dlgp2Transformer())

    @classmethod
    def instance(cls) -> "Dlgp2Parser":
        if not cls._instance:
            cls._instance = Dlgp2Parser()
        return cls._instance

    def parse_all(self, to_parse: str, filter_fun: Callable[[object], bool] = None) -> Iterable[object]:
        return self._parse_all(self._parser.parse(to_parse)["body"], filter_fun)  # type: ignore

    def parse_all_from_file(self, file_path: str, filter_fun: Callable[[object], bool] = None) -> Iterable[object]:
        with open(file_path, "r") as file:
            return self.parse_all(file.read(), filter_fun)

    @staticmethod
    def _parse_all(parsing_result: dict, filter_fun: Callable[[object], bool] = None) -> Iterable[object]:
        objects = set()

        for e in parsing_result:
            if not filter_fun or filter_fun(e):
                match e:
                    case AtomSet():
                        objects.update(e)
                    case _:
                        objects.add(e)

        return objects

    def parse_atoms(self, to_parse: str) -> MutableAtomSet:
        return MutableAtomSet(
            [atom for atom in self.parse_all(to_parse, lambda x: isinstance(x, AtomSet))])  # type: ignore

    def parse_atoms_from_file(self, file_path: str) -> MutableAtomSet:
        return MutableAtomSet(
            [atom for atom in self.parse_all_from_file(file_path, lambda x: isinstance(x, AtomSet))])  # type: ignore

    def parse_negative_constraints(self, to_parse: str) -> Iterable[NegativeConstraint]:
        return set([nc for nc in self.parse_all(to_parse, lambda x: isinstance(x, NegativeConstraint))])  # type: ignore

    def parse_negative_constraints_from_file(self, file_path: str) -> Iterable[NegativeConstraint]:
        return set(  # type: ignore
            [nc for nc in self.parse_all_from_file(file_path,
                                                   lambda x: isinstance(x, NegativeConstraint))])

    def parse_rules(self, to_parse: str) -> Iterable[Rule]:
        return set([nc for nc in self.parse_all(to_parse, lambda x: isinstance(x, Rule))])  # type: ignore

    def parse_rules_from_file(self, file_path: str) -> Iterable[Rule]:
        return set([nc for nc in self.parse_all_from_file(file_path, lambda x: isinstance(x, Rule))])  # type: ignore

    def parse_conjunctive_queries(self, to_parse: str) -> Iterable[ConjunctiveQuery]:
        return set(nc for nc in self.parse_all(to_parse, lambda x: isinstance(x, ConjunctiveQuery)))  # type: ignore

    def parse_union_conjunctive_queries(self, to_parse: str) -> Iterable[UnionConjunctiveQueries]:
        for query in self.parse_all(to_parse, lambda x: isinstance(x, UnionConjunctiveQueries)
                                                        or isinstance(x, ConjunctiveQuery)):
            if isinstance(query, UnionConjunctiveQueries):
                yield query
            else:
                yield UnionConjunctiveQueries([query], query.answer_variables, query.label)

    def parse_union_conjunctive_queries_from_file(self, file_path: str) -> Iterable[UnionConjunctiveQueries]:
        for query in self.parse_all_from_file(file_path, lambda x: isinstance(x, UnionConjunctiveQueries)
                                                        or isinstance(x, ConjunctiveQuery)):
            if isinstance(query, UnionConjunctiveQueries):
                yield query
            else:
                yield UnionConjunctiveQueries([query], query.answer_variables, query.label)

    def parse_conjunctive_queries_from_file(self, file_path: str) -> Iterable[ConjunctiveQuery]:
        return set(  # type: ignore
            [nc for nc in self.parse_all_from_file(file_path,
                                                   lambda x: isinstance(x, ConjunctiveQuery))])
