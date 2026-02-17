"""Triple store storage backed by RDFLib graph."""

from __future__ import annotations

from typing import Iterable, Iterator, Set, cast

from rdflib import BNode, Graph, Literal as RDFLiteral, URIRef
from rdflib.namespace import RDF
from rdflib.term import Literal as RDFTermLiteral
from rdflib.term import Node

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.blank_node_term import BlankNodeTerm
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.atomic_pattern import UnconstrainedPattern
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.schema import (
    LogicalType,
    PositionSpec,
    RelationSchema,
    SchemaAware,
)
from prototyping_inference_engine.api.fact_base.fact_base import FactBase
from prototyping_inference_engine.api.data.storage.acceptance import AcceptanceResult
from prototyping_inference_engine.api.data.storage.protocols import AtomAcceptance
from prototyping_inference_engine.api.fact_base.protocols import Writable


class TripleStoreStorage(FactBase, Writable, AtomAcceptance, SchemaAware):
    """RDF triple-store wrapper with unary and binary atom mapping."""

    def __init__(self, graph: Graph | None = None):
        self._graph = graph if graph is not None else Graph()

    @staticmethod
    def _term_to_node(term: Term) -> Node:
        if isinstance(term, Variable):
            raise ValueError("Variables cannot be stored in triple storage")
        if isinstance(term, Literal):
            lexical = term.lexical if term.lexical is not None else str(term.value)
            return RDFLiteral(lexical, datatype=term.datatype, lang=term.lang)
        identifier = str(term.identifier)
        if identifier.startswith("_:"):
            return BNode(identifier[2:])
        return URIRef(identifier)

    @staticmethod
    def _node_to_term(node: Node) -> Term:
        if isinstance(node, RDFTermLiteral):
            lexical = cast(str, node)
            datatype = str(node.datatype) if node.datatype is not None else None
            lang = node.language
            comparison_key = (datatype, lexical, lang)
            return Literal(lexical, datatype, lexical, lang, comparison_key)
        if isinstance(node, BNode):
            return BlankNodeTerm(f"_:{str(node)}")
        return Constant(str(node))

    @staticmethod
    def _predicate_to_iri(predicate: Predicate) -> URIRef:
        return URIRef(predicate.name)

    def _atom_to_triple(self, atom: Atom) -> tuple[Node, URIRef, Node]:
        if atom.predicate.arity == 1:
            subject = self._term_to_node(atom.terms[0])
            unary_object = self._predicate_to_iri(Predicate(atom.predicate.name, 1))
            return subject, RDF.type, unary_object
        if atom.predicate.arity == 2:
            subject = self._term_to_node(atom.terms[0])
            binary_object: Node = self._term_to_node(atom.terms[1])
            return subject, self._predicate_to_iri(atom.predicate), binary_object
        raise ValueError("Triple storage only supports arity 1 or 2")

    def accepts_predicate(self, predicate: Predicate) -> AcceptanceResult:
        if predicate.arity not in (1, 2):
            return AcceptanceResult.reject(
                f"Predicate {predicate} has arity {predicate.arity}; expected 1 or 2"
            )
        return AcceptanceResult.ok()

    def accepts_atom(self, atom: Atom) -> AcceptanceResult:
        predicate_acceptance = self.accepts_predicate(atom.predicate)
        if not predicate_acceptance.accepted:
            return predicate_acceptance
        if any(isinstance(term, Variable) for term in atom.terms):
            return AcceptanceResult.reject(
                "Triple storage does not accept variables in stored atoms"
            )
        return AcceptanceResult.ok()

    def get_predicates(self) -> Iterator[Predicate]:
        predicates: Set[Predicate] = set()
        for subject, pred, obj in self._graph.triples((None, None, None)):
            if pred == RDF.type and isinstance(obj, URIRef):
                predicates.add(Predicate(str(obj), 1))
            else:
                predicates.add(Predicate(str(pred), 2))
        return iter(predicates)

    def has_predicate(self, predicate: Predicate) -> bool:
        if predicate.arity == 1:
            return any(
                True
                for _ in self._graph.triples(
                    (None, RDF.type, self._predicate_to_iri(predicate))
                )
            )
        if predicate.arity == 2:
            return any(
                True
                for _ in self._graph.triples(
                    (None, self._predicate_to_iri(predicate), None)
                )
            )
        return False

    def get_atomic_pattern(self, predicate: Predicate) -> UnconstrainedPattern:
        return UnconstrainedPattern(predicate)

    def get_schema(self, predicate: Predicate) -> RelationSchema | None:
        if predicate.arity == 1:
            return RelationSchema(
                predicate,
                (PositionSpec(name="subject", logical_type=LogicalType.IRI),),
            )
        if predicate.arity == 2:
            return RelationSchema(
                predicate,
                (
                    PositionSpec(name="subject", logical_type=LogicalType.IRI),
                    PositionSpec(name="object", logical_type=LogicalType.UNKNOWN),
                ),
            )
        return None

    def get_schemas(self) -> Iterable[RelationSchema]:
        for predicate in self.get_predicates():
            schema = self.get_schema(predicate)
            if schema is not None:
                yield schema

    def can_evaluate(self, query: BasicQuery) -> bool:
        return query.predicate.arity in (1, 2)

    def evaluate(self, query: BasicQuery) -> Iterator[tuple[Term, ...]]:
        if query.predicate.arity not in (1, 2):
            raise ValueError(
                f"Predicate {query.predicate} arity {query.predicate.arity} is unsupported"
            )

        answer_positions = sorted(query.answer_variables.keys())

        if query.predicate.arity == 1:
            unary_subject: Node | None = None
            bound0 = query.get_bound_term(0)
            if bound0 is not None:
                unary_subject = self._term_to_node(bound0)
            triples = self._graph.triples(
                (unary_subject, RDF.type, self._predicate_to_iri(query.predicate))
            )
            for s, _, _ in triples:
                candidate = [self._node_to_term(s)]
                yield tuple(candidate[pos] for pos in answer_positions)
            return

        subject: Node | None = None
        object_node: Node | None = None
        bound0 = query.get_bound_term(0)
        bound1 = query.get_bound_term(1)
        if bound0 is not None:
            subject = self._term_to_node(bound0)
        if bound1 is not None:
            object_node = self._term_to_node(bound1)

        triples = self._graph.triples(
            (subject, self._predicate_to_iri(query.predicate), object_node)
        )
        for s, _, o in triples:
            candidate = [self._node_to_term(s), self._node_to_term(o)]
            yield tuple(candidate[pos] for pos in answer_positions)

    @property
    def variables(self) -> Set[Variable]:
        return set()

    @property
    def constants(self) -> Set[Constant]:
        constants: Set[Constant] = set()
        for atom in self:
            constants.update(atom.constants)
        return constants

    @property
    def terms(self) -> Set[Term]:
        terms: Set[Term] = set()
        for atom in self:
            terms.update(atom.terms)
        return terms

    def add(self, atom: Atom) -> None:
        acceptance = self.accepts_atom(atom)
        if not acceptance.accepted:
            raise ValueError(acceptance.reason)
        self._graph.add(self._atom_to_triple(atom))

    def update(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.add(atom)

    def remove(self, atom: Atom) -> None:
        acceptance = self.accepts_atom(atom)
        if not acceptance.accepted:
            return
        self._graph.remove(self._atom_to_triple(atom))

    def remove_all(self, atoms: Iterable[Atom]) -> None:
        for atom in atoms:
            self.remove(atom)

    def __iter__(self) -> Iterator[Atom]:
        for s, p, o in self._graph.triples((None, None, None)):
            if p == RDF.type and isinstance(o, URIRef):
                yield Atom(Predicate(str(o), 1), self._node_to_term(s))
            else:
                yield Atom(
                    Predicate(str(p), 2),
                    self._node_to_term(s),
                    self._node_to_term(o),
                )

    def __len__(self) -> int:
        return len(self._graph)

    def __contains__(self, atom: Atom) -> bool:
        acceptance = self.accepts_atom(atom)
        if not acceptance.accepted:
            return False
        return self._atom_to_triple(atom) in self._graph
