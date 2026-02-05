"""IRI normalization utilities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable
import re
import unicodedata


class RFCNormalizationScheme(Enum):
    STRING = auto()
    CASE = auto()
    CHARACTER = auto()
    PCT = auto()
    SCHEME = auto()
    PATH = auto()
    SYNTAX = auto()


class IRINormalizer:
    """Interface for IRI normalization."""

    def normalize_scheme(self, scheme: str | None) -> str | None:
        return scheme

    def normalize_user_info(
        self, userinfo: str | None, scheme: str | None
    ) -> str | None:
        return userinfo

    def normalize_host(self, host: str | None) -> str | None:
        return host

    def normalize_port(self, port: str | None, scheme: str | None) -> str | None:
        return port

    def normalize_path(self, path: str, scheme: str | None, has_authority: bool) -> str:
        return path

    def normalize_query(self, query: str | None, scheme: str | None) -> str | None:
        return query

    def normalize_fragment(
        self, fragment: str | None, scheme: str | None
    ) -> str | None:
        return fragment


_UNRESERVED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
_RESERVED = set(":/?#[]@!$&'()*+,;=")


def _is_unreserved(char: str) -> bool:
    return char in _UNRESERVED


def _is_iunreserved(char: str) -> bool:
    if _is_unreserved(char):
        return True
    if char in _RESERVED:
        return False
    if ord(char) < 0x80:
        return False
    # Approximate RFC 3987 ucschar/iprivate: allow any non-control Unicode char
    codepoint = ord(char)
    if codepoint <= 0x20 or codepoint == 0x7F:
        return False
    return True


def _nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _uppercase_pct(input_value: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return match.group(0).upper()

    return re.sub(r"%[0-9A-Fa-f]{2}", repl, input_value)


def _normalize_pct_standard(value: str, uppercase: bool) -> str:
    output: list[str] = []
    i = 0
    length = len(value)
    while i < length:
        char = value[i]
        if char == "%" and i + 2 < length and _is_hex_pair(value[i + 1 : i + 3]):
            byte_value = int(value[i + 1 : i + 3], 16)
            decoded = chr(byte_value)
            if _is_unreserved(decoded):
                output.append(decoded)
            else:
                hex_pair = value[i + 1 : i + 3]
                output.append(
                    "%" + (hex_pair.upper() if uppercase else hex_pair.lower())
                )
            i += 3
            continue
        output.append(char)
        i += 1
    return "".join(output)


def _normalize_pct_extended(value: str, uppercase: bool) -> str:
    output: list[str] = []
    i = 0
    length = len(value)
    while i < length:
        if value[i] != "%" or i + 2 >= length or not _is_hex_pair(value[i + 1 : i + 3]):
            output.append(value[i])
            i += 1
            continue

        bytes_run: list[int] = []
        while i + 2 < length and value[i] == "%" and _is_hex_pair(value[i + 1 : i + 3]):
            bytes_run.append(int(value[i + 1 : i + 3], 16))
            i += 3

        output.append(_decode_utf8_run(bytes_run, uppercase))

    return "".join(output)


def _decode_utf8_run(bytes_run: list[int], uppercase: bool) -> str:
    output: list[str] = []
    index = 0
    while index < len(bytes_run):
        first = bytes_run[index]
        width = _utf8_sequence_length(first)
        if width == 1:
            decoded = chr(first)
            if _is_iunreserved(decoded):
                output.append(decoded)
            else:
                output.append(_format_pct(first, uppercase))
            index += 1
            continue

        if width == 0 or index + width > len(bytes_run):
            output.append(_format_pct(first, uppercase))
            index += 1
            continue

        seq = bytes(bytes_run[index : index + width])
        try:
            decoded = seq.decode("utf-8")
        except UnicodeDecodeError:
            output.append(_format_pct(first, uppercase))
            index += 1
            continue

        if all(_is_iunreserved(ch) for ch in decoded):
            output.append(decoded)
        else:
            output.extend(_format_pct(b, uppercase) for b in seq)
        index += width

    return "".join(output)


def _format_pct(value: int, uppercase: bool) -> str:
    hex_value = f"{value:02x}"
    return f"%{hex_value.upper() if uppercase else hex_value}"


def _utf8_sequence_length(first: int) -> int:
    if first <= 0x7F:
        return 1
    if 0xC2 <= first <= 0xDF:
        return 2
    if 0xE0 <= first <= 0xEF:
        return 3
    if 0xF0 <= first <= 0xF4:
        return 4
    return 0


def _is_hex_pair(value: str) -> bool:
    return len(value) == 2 and all(c in "0123456789ABCDEFabcdef" for c in value)


_DEFAULT_PORTS = {
    "http": "80",
    "https": "443",
    "ftp": "21",
    "ws": "80",
    "wss": "443",
}


@dataclass
class StandardComposableNormalizer(IRINormalizer):
    schemes: set[RFCNormalizationScheme]

    def __init__(
        self, *schemes: RFCNormalizationScheme | Iterable[RFCNormalizationScheme]
    ):
        requested: list[RFCNormalizationScheme] = []
        for scheme in schemes:
            if isinstance(scheme, RFCNormalizationScheme):
                requested.append(scheme)
            else:
                requested.extend(list(scheme))
        self.schemes = _expand_schemes(requested)

    def has(self, scheme: RFCNormalizationScheme) -> bool:
        return scheme in self.schemes

    def normalize_scheme(self, scheme: str | None) -> str | None:
        if scheme is None:
            return None
        if self.has(RFCNormalizationScheme.CASE):
            return scheme.lower()
        return scheme

    def normalize_user_info(
        self, userinfo: str | None, scheme: str | None
    ) -> str | None:
        if userinfo is None:
            return None
        result = userinfo
        if self.has(RFCNormalizationScheme.PCT):
            result = _normalize_pct_standard(
                result, uppercase=self.has(RFCNormalizationScheme.CASE)
            )
        if self.has(RFCNormalizationScheme.CHARACTER):
            result = _nfc(result)
        return result

    def normalize_host(self, host: str | None) -> str | None:
        if host is None:
            return None
        result = host
        if self.has(RFCNormalizationScheme.PCT):
            result = _normalize_pct_standard(
                result, uppercase=self.has(RFCNormalizationScheme.CASE)
            )
        if self.has(RFCNormalizationScheme.CHARACTER):
            result = _nfc(result)
        if self.has(RFCNormalizationScheme.CASE):
            result = result.lower()
            if self.has(RFCNormalizationScheme.PCT):
                result = _uppercase_pct(result)
        return result

    def normalize_port(self, port: str | None, scheme: str | None) -> str | None:
        if port is None:
            return None
        if self.has(RFCNormalizationScheme.SCHEME):
            if scheme and scheme.lower() in _DEFAULT_PORTS:
                if port == _DEFAULT_PORTS[scheme.lower()]:
                    return None
        return port

    def normalize_path(self, path: str, scheme: str | None, has_authority: bool) -> str:
        result = path
        if has_authority and result == "":
            result = "/"
        if self.has(RFCNormalizationScheme.PCT):
            result = _normalize_pct_standard(
                result, uppercase=self.has(RFCNormalizationScheme.CASE)
            )
        if self.has(RFCNormalizationScheme.CHARACTER):
            result = _nfc(result)
        if self.has(RFCNormalizationScheme.PATH) and scheme is not None:
            from prototyping_inference_engine.iri.resolution import remove_dot_segments

            result = remove_dot_segments(result)
        return result

    def normalize_query(self, query: str | None, scheme: str | None) -> str | None:
        if query is None:
            return None
        result = query
        if self.has(RFCNormalizationScheme.PCT) and self.has(
            RFCNormalizationScheme.CASE
        ):
            result = _uppercase_pct(result)
        if self.has(RFCNormalizationScheme.CHARACTER):
            result = _nfc(result)
        return result

    def normalize_fragment(
        self, fragment: str | None, scheme: str | None
    ) -> str | None:
        if fragment is None:
            return None
        result = fragment
        if self.has(RFCNormalizationScheme.PCT) and self.has(
            RFCNormalizationScheme.CASE
        ):
            result = _uppercase_pct(result)
        if self.has(RFCNormalizationScheme.CHARACTER):
            result = _nfc(result)
        return result


class ExtendedComposableNormalizer(StandardComposableNormalizer):
    def normalize_user_info(
        self, userinfo: str | None, scheme: str | None
    ) -> str | None:
        if userinfo is None:
            return None
        result = userinfo
        if self.has(RFCNormalizationScheme.PCT):
            result = _normalize_pct_extended(
                result, uppercase=self.has(RFCNormalizationScheme.CASE)
            )
        if self.has(RFCNormalizationScheme.CHARACTER):
            result = _nfc(result)
        return result

    def normalize_host(self, host: str | None) -> str | None:
        if host is None:
            return None
        result = host
        if self.has(RFCNormalizationScheme.PCT):
            result = _normalize_pct_extended(
                result, uppercase=self.has(RFCNormalizationScheme.CASE)
            )
        if self.has(RFCNormalizationScheme.CHARACTER):
            result = _nfc(result)
        if self.has(RFCNormalizationScheme.CASE):
            result = result.lower()
            if self.has(RFCNormalizationScheme.PCT):
                result = _uppercase_pct(result)
        return result

    def normalize_path(self, path: str, scheme: str | None, has_authority: bool) -> str:
        result = path
        if has_authority and result == "":
            result = "/"
        if self.has(RFCNormalizationScheme.PCT):
            result = _normalize_pct_extended(
                result, uppercase=self.has(RFCNormalizationScheme.CASE)
            )
        if self.has(RFCNormalizationScheme.CHARACTER):
            result = _nfc(result)
        if self.has(RFCNormalizationScheme.PATH) and scheme is not None:
            from prototyping_inference_engine.iri.resolution import remove_dot_segments

            result = remove_dot_segments(result)
        return result


def _expand_schemes(
    requested: Iterable[RFCNormalizationScheme],
) -> set[RFCNormalizationScheme]:
    schemes: set[RFCNormalizationScheme] = set()
    for scheme in requested:
        if scheme == RFCNormalizationScheme.SYNTAX:
            schemes.update(
                {
                    RFCNormalizationScheme.CASE,
                    RFCNormalizationScheme.CHARACTER,
                    RFCNormalizationScheme.PCT,
                }
            )
        else:
            schemes.add(scheme)
    return schemes
