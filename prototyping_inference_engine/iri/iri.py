"""IRI parsing and manipulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from prototyping_inference_engine.iri.normalization import IRINormalizer
from prototyping_inference_engine.iri.preparator import StringPreparator
from prototyping_inference_engine.iri.resolution import (
    merge_paths,
    parse_iri_reference,
    remove_dot_segments,
    recompose,
)


class IRIParseError(ValueError):
    """Raised when parsing an IRI fails."""


_SCHEME_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-."


def _is_valid_scheme(value: str) -> bool:
    if not value:
        return False
    if not value[0].isalpha():
        return False
    return all(c in _SCHEME_CHARS for c in value)


def _split_authority(
    authority: str,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    userinfo = None
    hostport = authority
    if "@" in authority:
        userinfo, hostport = authority.rsplit("@", 1)

    host = hostport
    port = None

    if hostport.startswith("["):
        end = hostport.find("]")
        if end != -1:
            host = hostport[: end + 1]
            rest = hostport[end + 1 :]
            if rest.startswith(":"):
                port = rest[1:] or None
        else:
            host = hostport
    elif ":" in hostport:
        host, port_candidate = hostport.rsplit(":", 1)
        if port_candidate.isdigit():
            port = port_candidate
        else:
            host = hostport
            port = None

    return userinfo, host or None, port


@dataclass
class IRIRef:
    scheme: Optional[str]
    authority: Optional[str]
    path: str
    query: Optional[str]
    fragment: Optional[str]
    has_authority: bool

    def __init__(
        self,
        iri: str,
        preparator: Optional[StringPreparator] = None,
    ) -> None:
        value = preparator.transform(iri) if preparator else iri
        self._parse(value)

    def _parse(self, value: str) -> None:
        if value.count("#") > 1:
            raise IRIParseError(f"Invalid IRI reference: {value}")

        if value.startswith(":") or value.startswith("://"):
            raise IRIParseError(f"Invalid IRI reference: {value}")

        # Identify scheme if present before any '/', '?', '#'
        first_colon = value.find(":")
        first_slash = value.find("/")
        first_q = value.find("?")
        first_hash = value.find("#")
        first_sep = (
            min(x for x in (first_slash, first_q, first_hash) if x != -1)
            if any(x != -1 for x in (first_slash, first_q, first_hash))
            else -1
        )

        scheme = None
        rest = value
        if first_colon != -1 and (first_sep == -1 or first_colon < first_sep):
            candidate = value[:first_colon]
            if not _is_valid_scheme(candidate):
                raise IRIParseError(f"Invalid IRI scheme: {candidate}")
            scheme = candidate
            rest = value[first_colon + 1 :]

        parts = parse_iri_reference(rest)

        if scheme is None and parts.scheme is not None:
            scheme = parts.scheme

        self.scheme = scheme
        self.authority = parts.authority
        self.path = parts.path
        self.query = parts.query
        self.fragment = parts.fragment
        self.has_authority = parts.has_authority

    def is_absolute(self) -> bool:
        return self.scheme is not None

    def is_relative(self) -> bool:
        return self.scheme is None

    def has_query(self) -> bool:
        return self.query is not None

    def has_rooted_path(self) -> bool:
        return self.path.startswith("/")

    def recompose(self) -> str:
        return recompose(
            self.scheme,
            self.authority,
            self.path,
            self.query,
            self.fragment,
            self.has_authority,
        )

    def __str__(self) -> str:
        return self.recompose()

    def copy(self) -> "IRIRef":
        clone = object.__new__(IRIRef)
        clone.scheme = self.scheme
        clone.authority = self.authority
        clone.path = self.path
        clone.query = self.query
        clone.fragment = self.fragment
        clone.has_authority = self.has_authority
        return clone

    def resolve_in_place(self, base: "IRIRef", strict: bool = True) -> "IRIRef":
        if base is None:
            raise ValueError("Base IRI is required for resolution")
        if base.scheme is None:
            raise ValueError("Base IRI must be absolute")

        ref = self.copy()

        if not strict and ref.scheme == base.scheme:
            ref.scheme = None

        if ref.scheme is not None:
            self.scheme = ref.scheme
            self.authority = ref.authority
            self.path = remove_dot_segments(ref.path)
            self.query = ref.query
            self.fragment = ref.fragment
            self.has_authority = ref.has_authority
            return self

        if ref.has_authority:
            self.scheme = base.scheme
            self.authority = ref.authority
            self.path = remove_dot_segments(ref.path)
            self.query = ref.query
            self.fragment = ref.fragment
            self.has_authority = True
            return self

        if ref.path == "":
            self.path = base.path
            self.query = ref.query if ref.query is not None else base.query
        else:
            if ref.path.startswith("/"):
                self.path = remove_dot_segments(ref.path)
            else:
                self.path = remove_dot_segments(
                    merge_paths(base.path, base.has_authority, ref.path)
                )
            self.query = ref.query

        self.scheme = base.scheme
        self.authority = base.authority
        self.fragment = ref.fragment
        self.has_authority = base.has_authority
        return self

    def resolve(self, base: "IRIRef", strict: bool = True) -> "IRIRef":
        return self.copy().resolve_in_place(base, strict)

    def normalize_in_place(self, normalizer: IRINormalizer) -> "IRIRef":
        scheme = normalizer.normalize_scheme(self.scheme)
        authority = self.authority
        has_authority = self.has_authority
        userinfo = None
        host = None
        port = None
        if authority is not None or has_authority:
            userinfo, host, port = _split_authority(authority or "")
            userinfo = normalizer.normalize_user_info(userinfo, scheme)
            host = normalizer.normalize_host(host)
            port = normalizer.normalize_port(port, scheme)
            authority = _recompose_authority(userinfo, host, port)
            if authority == "" and has_authority:
                authority = ""

        path = normalizer.normalize_path(self.path, scheme, has_authority)
        query = normalizer.normalize_query(self.query, scheme)
        fragment = normalizer.normalize_fragment(self.fragment, scheme)

        self.scheme = scheme
        self.authority = authority
        self.path = path
        self.query = query
        self.fragment = fragment
        self.has_authority = has_authority
        return self

    def normalize(self, normalizer: IRINormalizer) -> "IRIRef":
        return self.copy().normalize_in_place(normalizer)

    def relativize(self, base: "IRIRef") -> "IRIRef":
        if not base.is_absolute():
            raise ValueError(
                "IRI relativisation requires an absolute base (with a scheme and no fragment)."
            )
        if self.is_relative():
            raise ValueError("IRI relativisation requires an absolute IRI.")

        if self.scheme != base.scheme or (
            self.authority is None and base.authority is not None
        ):
            return self.copy()

        if self.authority is not None and self.authority != base.authority:
            return IRIRef.from_components(
                None,
                self.authority,
                self.path,
                self.query,
                self.fragment,
                has_authority=True,
            )

        if (
            self.authority is None
            and not self.has_rooted_path()
            and base.has_rooted_path()
        ):
            return self.copy()

        must_find_path = self.query is None and base.query is not None
        relative_path = _relativize_path(base.path, self.path, must_find_path)

        if relative_path is None:
            if self.authority is None:
                return self.copy()
            return IRIRef.from_components(
                None,
                self.authority,
                self.path,
                self.query,
                self.fragment,
                has_authority=True,
            )

        candidate = IRIRef.from_components(
            None,
            None,
            relative_path,
            self.query,
            self.fragment,
            has_authority=False,
        )

        if (
            candidate.recompose() == ""
            and self.query is not None
            and self.query == base.query
        ):
            return IRIRef.from_components(
                None,
                None,
                relative_path,
                None,
                self.fragment,
                has_authority=False,
            )

        if len(candidate.recompose()) >= len(self.recompose()):
            if self.authority is None:
                return self.copy()
            network = IRIRef.from_components(
                None,
                self.authority,
                self.path,
                self.query,
                self.fragment,
                has_authority=True,
            )
            if len(network.recompose()) < len(self.recompose()):
                return network
            return self.copy()

        return candidate

    @classmethod
    def from_components(
        cls,
        scheme: Optional[str],
        authority: Optional[str],
        path: str,
        query: Optional[str],
        fragment: Optional[str],
        has_authority: bool,
    ) -> "IRIRef":
        instance = object.__new__(cls)
        instance.scheme = scheme
        instance.authority = authority
        instance.path = path
        instance.query = query
        instance.fragment = fragment
        instance.has_authority = has_authority
        return instance


def _recompose_authority(
    userinfo: Optional[str],
    host: Optional[str],
    port: Optional[str],
) -> Optional[str]:
    if userinfo is None and host is None and port is None:
        return None
    result = ""
    if userinfo:
        result += f"{userinfo}@"
    if host:
        result += host
    if port:
        result += f":{port}"
    return result


def _relativize_path(
    base_path: str, target_path: str, must_find_path: bool
) -> Optional[str]:
    if target_path.startswith("/"):
        # Absolute path reference
        if base_path.startswith("/"):
            # can still compute relative
            pass
        else:
            return target_path

    base_segments = _split_path_segments(base_path)
    target_segments = _split_path_segments(target_path)

    if base_path.endswith("/") and base_segments and base_segments[-1] == "":
        base_segments = base_segments[:-1]

    if not base_path.endswith("/") and base_segments:
        base_segments = base_segments[:-1]

    common = 0
    for base_seg, target_seg in zip(base_segments, target_segments):
        if base_seg != target_seg:
            break
        common += 1

    rel_segments = [".."] * (len(base_segments) - common) + target_segments[common:]

    if rel_segments == [""]:
        rel_segments = []

    relative = "/".join(rel_segments)
    if target_path.endswith("/") and relative and not relative.endswith("/"):
        relative += "/"

    if relative == "" and must_find_path:
        return None

    return relative


def _split_path_segments(path: str) -> list[str]:
    if path == "":
        return []
    if path.startswith("/"):
        path = path[1:]
    segments = path.split("/")
    return segments
