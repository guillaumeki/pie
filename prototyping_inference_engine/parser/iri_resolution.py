"""
Backward-compatible wrappers for IRI resolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from prototyping_inference_engine.iri.iri import IRIRef
from prototyping_inference_engine.iri.resolution import remove_dot_segments


@dataclass(frozen=True)
class IriReference:
    scheme: Optional[str]
    authority: Optional[str]
    path: str
    query: Optional[str]
    fragment: Optional[str]


def parse_iri_reference(value: str) -> IriReference:
    iri = IRIRef(value)
    return IriReference(
        scheme=iri.scheme,
        authority=iri.authority,
        path=iri.path,
        query=iri.query,
        fragment=iri.fragment,
    )


def is_absolute_iri(value: str) -> bool:
    return IRIRef(value).is_absolute()


def resolve_iri_reference(
    reference: str, base: Optional[str], strict: bool = True
) -> str:
    if base is None or base == "":
        return reference
    base_iri = IRIRef(base)
    return IRIRef(reference).resolve(base_iri, strict).recompose()


__all__ = [
    "IriReference",
    "parse_iri_reference",
    "is_absolute_iri",
    "resolve_iri_reference",
    "remove_dot_segments",
]
