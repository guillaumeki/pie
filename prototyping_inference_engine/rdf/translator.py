"""
RDF translation primitives independent from IO.
"""

# References:
# - "RDF 1.1 Concepts and Abstract Syntax" —
#   Richard Cyganiak, David Wood, Markus Lanthaler.
#   Link: https://www.w3.org/TR/rdf11-concepts/
#
# Summary:
# RDF graphs are sets of triples with IRIs, literals, and blank nodes; translators
# map between RDF terms and application-specific representations.
#
# Properties used here:
# - RDF term model and graph semantics.
#
# Implementation notes:
# This module implements translation modes that map RDF triples to PIE atoms.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from rdflib import BNode, Literal as RDFLiteral, URIRef  # type: ignore[import-not-found]

from prototyping_inference_engine.api.atom.atom import Atom
from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.term import Term
from prototyping_inference_engine.session.term_factories import TermFactories


class RDFTranslationMode(str, Enum):
    RAW = "raw"
    NATURAL = "natural"
    NATURAL_FULL = "natural_full"

    @classmethod
    def from_string(cls, value: str) -> "RDFTranslationMode":
        normalized = value.strip().lower()
        for mode in cls:
            if mode.value == normalized:
                return mode
        raise ValueError(f"Unknown RDF translation mode: {value}")


@dataclass(frozen=True)
class RDFTranslationContext:
    term_factories: TermFactories


class RDFTranslator:
    def __init__(self, context: RDFTranslationContext) -> None:
        self._context = context

    def statement_to_atom(self, subject, predicate, obj) -> Atom:
        raise NotImplementedError

    def atom_to_triples(self, atom: Atom) -> Iterable[tuple[object, object, object]]:
        raise NotImplementedError

    def _predicate(self, name: str, arity: int) -> Predicate:
        from prototyping_inference_engine.api.atom.predicate import Predicate as Pred

        if self._context.term_factories.has(Pred):
            return self._context.term_factories.get(Pred).create(name, arity)
        return Pred(name, arity)

    def _constant(self, identifier: object) -> Constant:
        if self._context.term_factories.has(Constant):
            return self._context.term_factories.get(Constant).create(identifier)
        return Constant(identifier)

    def _literal(
        self, lexical: str, datatype: str | None = None, lang: str | None = None
    ) -> Literal:
        from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
            LiteralFactory,
        )

        if self._context.term_factories.has(Literal):
            literal_factory: LiteralFactory = self._context.term_factories.get(Literal)
            return literal_factory.create(lexical, datatype, lang)
        return Literal(lexical, datatype, lexical, lang, lexical)

    def _to_term(self, value) -> Term:
        if isinstance(value, RDFLiteral):
            datatype = str(value.datatype) if value.datatype else None
            lang = value.language
            return self._literal(str(value), datatype, lang)
        if isinstance(value, URIRef):
            return self._constant(str(value))
        if isinstance(value, BNode):
            return self._constant(f"_:{value}")
        return self._constant(str(value))

    @staticmethod
    def _term_to_rdf(term: Term):
        if isinstance(term, Literal):
            datatype = URIRef(term.datatype) if term.datatype else None
            return RDFLiteral(term.value, lang=term.lang, datatype=datatype)
        if isinstance(term, Constant):
            identifier = str(term.identifier)
            if identifier.startswith("_:"):
                return BNode(identifier[2:])
            return URIRef(identifier)
        return RDFLiteral(str(term))


class RawRDFTranslator(RDFTranslator):
    def statement_to_atom(self, subject, predicate, obj) -> Atom:
        pred = self._predicate("triple", 3)
        return Atom(
            pred, self._to_term(subject), self._to_term(predicate), self._to_term(obj)
        )

    def atom_to_triples(self, atom: Atom) -> Iterable[tuple[object, object, object]]:
        if atom.predicate.arity != 3 or atom.predicate.name != "triple":
            return []
        subject, predicate, obj = atom.terms
        return [
            (
                self._term_to_rdf(subject),
                self._term_to_rdf(predicate),
                self._term_to_rdf(obj),
            )
        ]


class NaturalRDFTranslator(RDFTranslator):
    def statement_to_atom(self, subject, predicate, obj) -> Atom:
        pred = self._predicate(str(predicate), 2)
        return Atom(pred, self._to_term(subject), self._to_term(obj))

    def atom_to_triples(self, atom: Atom) -> Iterable[tuple[object, object, object]]:
        if atom.predicate.arity != 2:
            return []
        subject, obj = atom.terms
        predicate = URIRef(atom.predicate.name)
        return [(self._term_to_rdf(subject), predicate, self._term_to_rdf(obj))]


class NaturalFullRDFTranslator(RDFTranslator):
    _RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

    def statement_to_atom(self, subject, predicate, obj) -> Atom:
        if str(predicate) == self._RDF_TYPE:
            class_name = str(self._to_term(obj))
            pred = self._predicate(class_name, 1)
            return Atom(pred, self._to_term(subject))
        pred = self._predicate(str(predicate), 2)
        return Atom(pred, self._to_term(subject), self._to_term(obj))

    def atom_to_triples(self, atom: Atom) -> Iterable[tuple[object, object, object]]:
        if atom.predicate.arity == 1:
            rdf_subject = self._term_to_rdf(atom.terms[0])
            rdf_predicate = URIRef(self._RDF_TYPE)
            rdf_object = URIRef(atom.predicate.name)
            return [(rdf_subject, rdf_predicate, rdf_object)]
        if atom.predicate.arity == 2:
            subject_term, object_term = atom.terms
            rdf_predicate = URIRef(atom.predicate.name)
            return [
                (
                    self._term_to_rdf(subject_term),
                    rdf_predicate,
                    self._term_to_rdf(object_term),
                )
            ]
        return []
