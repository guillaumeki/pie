"""
IRI reference resolution utilities (RFC 3986).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import re


_IRI_REFERENCE_RE = re.compile(
    r"^(?:(?P<scheme>[A-Za-z][A-Za-z0-9+\-.]*):)?"
    r"(?:(?P<authority>//[^/?#]*))?"
    r"(?P<path>[^?#]*)"
    r"(?:\?(?P<query>[^#]*))?"
    r"(?:#(?P<fragment>.*))?$"
)


@dataclass(frozen=True)
class IriReferenceParts:
    scheme: Optional[str]
    authority: Optional[str]
    path: str
    query: Optional[str]
    fragment: Optional[str]
    has_authority: bool


def parse_iri_reference(value: str, *, allow_scheme: bool = True) -> IriReferenceParts:
    match = _IRI_REFERENCE_RE.match(value)
    if not match:
        return IriReferenceParts(None, None, value, None, None, False)
    authority = match.group("authority")
    has_authority = authority is not None
    if authority is not None and authority.startswith("//"):
        authority = authority[2:]
    scheme = match.group("scheme")
    path = match.group("path") or ""
    query = match.group("query")
    fragment = match.group("fragment")
    if not allow_scheme and scheme is not None and authority is None:
        path = f"{scheme}:{path}"
        scheme = None
    return IriReferenceParts(
        scheme=scheme,
        authority=authority,
        path=path,
        query=query,
        fragment=fragment,
        has_authority=has_authority,
    )


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


def merge_paths(base_path: str, base_has_authority: bool, ref_path: str) -> str:
    if base_has_authority and base_path == "":
        return "/" + ref_path
    slash_index = base_path.rfind("/")
    if slash_index == -1:
        return ref_path
    return base_path[: slash_index + 1] + ref_path


def _remove_last_segment(path: str) -> str:
    if path == "":
        return ""
    index = path.rfind("/")
    if index == -1:
        return ""
    return path[:index]


def recompose(
    scheme: Optional[str],
    authority: Optional[str],
    path: str,
    query: Optional[str],
    fragment: Optional[str],
    has_authority: bool,
) -> str:
    result = ""
    if scheme is not None:
        result += scheme + ":"
    if has_authority:
        result += "//" + (authority or "")
    result += path
    if query is not None:
        result += "?" + query
    if fragment is not None:
        result += "#" + fragment
    return result
