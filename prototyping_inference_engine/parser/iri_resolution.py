"""
IRI reference resolution utilities.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional


_IRI_REFERENCE_RE = re.compile(
    r"^(?:(?P<scheme>[A-Za-z][A-Za-z0-9+\-.]*):)?"
    r"(?:(?P<authority>//[^/?#]*))?"
    r"(?P<path>[^?#]*)"
    r"(?:\?(?P<query>[^#]*))?"
    r"(?:#(?P<fragment>.*))?$"
)


@dataclass(frozen=True)
class IriReference:
    scheme: Optional[str]
    authority: Optional[str]
    path: str
    query: Optional[str]
    fragment: Optional[str]


def parse_iri_reference(value: str) -> IriReference:
    match = _IRI_REFERENCE_RE.match(value)
    if not match:
        return IriReference(None, None, value, None, None)
    authority = match.group("authority")
    if authority is not None and authority.startswith("//"):
        authority = authority[2:]
    return IriReference(
        scheme=match.group("scheme"),
        authority=authority,
        path=match.group("path") or "",
        query=match.group("query"),
        fragment=match.group("fragment"),
    )


def is_absolute_iri(value: str) -> bool:
    return parse_iri_reference(value).scheme is not None


def resolve_iri_reference(
    reference: str, base: Optional[str], strict: bool = True
) -> str:
    if base is None or base == "":
        return reference

    ref = parse_iri_reference(reference)
    base_ref = parse_iri_reference(base)

    if base_ref.scheme is None:
        return reference

    if not strict and ref.scheme == base_ref.scheme:
        ref = IriReference(
            scheme=None,
            authority=ref.authority,
            path=ref.path,
            query=ref.query,
            fragment=ref.fragment,
        )

    if ref.scheme is not None:
        target = IriReference(
            scheme=ref.scheme,
            authority=ref.authority,
            path=remove_dot_segments(ref.path),
            query=ref.query,
            fragment=ref.fragment,
        )
        return recompose_iri(target)

    if ref.authority is not None:
        target = IriReference(
            scheme=base_ref.scheme,
            authority=ref.authority,
            path=remove_dot_segments(ref.path),
            query=ref.query,
            fragment=ref.fragment,
        )
        return recompose_iri(target)

    if ref.path == "":
        path = base_ref.path
        query = ref.query if ref.query is not None else base_ref.query
    else:
        if ref.path.startswith("/"):
            path = remove_dot_segments(ref.path)
        else:
            path = remove_dot_segments(_merge_paths(base_ref, ref.path))
        query = ref.query

    target = IriReference(
        scheme=base_ref.scheme,
        authority=base_ref.authority,
        path=path,
        query=query,
        fragment=ref.fragment,
    )
    return recompose_iri(target)


def _merge_paths(base: IriReference, ref_path: str) -> str:
    if base.authority is not None and base.path == "":
        return "/" + ref_path
    slash_index = base.path.rfind("/")
    if slash_index == -1:
        return ref_path
    return base.path[: slash_index + 1] + ref_path


def remove_dot_segments(path: str) -> str:
    input_buffer = path
    output = ""

    while input_buffer:
        if input_buffer.startswith("../"):
            input_buffer = input_buffer[3:]
        elif input_buffer.startswith("./"):
            input_buffer = input_buffer[2:]
        elif input_buffer.startswith("/./"):
            input_buffer = "/" + input_buffer[3:]
        elif input_buffer == "/.":
            input_buffer = "/"
        elif input_buffer.startswith("/../"):
            input_buffer = "/" + input_buffer[4:]
            output = _remove_last_segment(output)
        elif input_buffer == "/..":
            input_buffer = "/"
            output = _remove_last_segment(output)
        elif input_buffer in (".", ".."):
            input_buffer = ""
        else:
            next_slash = input_buffer.find(
                "/", 1 if input_buffer.startswith("/") else 0
            )
            if next_slash == -1:
                segment = input_buffer
                input_buffer = ""
            else:
                segment = input_buffer[:next_slash]
                input_buffer = input_buffer[next_slash:]
            output += segment

    return output


def _remove_last_segment(path: str) -> str:
    if path == "":
        return ""
    index = path.rfind("/")
    if index == -1:
        return ""
    return path[:index]


def recompose_iri(reference: IriReference) -> str:
    result = ""
    if reference.scheme is not None:
        result += reference.scheme + ":"
    if reference.authority is not None:
        result += "//" + reference.authority
    result += reference.path
    if reference.query is not None:
        result += "?" + reference.query
    if reference.fragment is not None:
        result += "#" + reference.fragment
    return result
