"""
Format detection helpers for @import.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FormatDetectionResult:
    format: str
    rdf_format_hint: str | None = None


_RDF_EXTENSIONS: dict[str, str | None] = {
    ".ttl": "turtle",
    ".nt": "nt",
    ".n3": "n3",
    ".rdf": "xml",
    ".xml": "xml",
    ".jsonld": "json-ld",
    ".trig": "trig",
    ".nq": "nquads",
}


def detect_format(path: Path, sample: str | None = None) -> FormatDetectionResult:
    suffix = path.suffix.lower()
    if suffix in {".dlgpe", ".dlgp"}:
        return FormatDetectionResult("dlgpe")
    if suffix in {".csv"}:
        return FormatDetectionResult("csv")
    if suffix in {".rls", ".rlscsv"}:
        return FormatDetectionResult("rls")
    if suffix in _RDF_EXTENSIONS:
        return FormatDetectionResult("rdf", _RDF_EXTENSIONS[suffix])

    if sample:
        for line in sample.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("%"):
                continue
            if stripped.startswith("@source") and "load-csv" in stripped:
                return FormatDetectionResult("rls")
            if stripped.startswith("@") or stripped.startswith("?("):
                return FormatDetectionResult("dlgpe")
            if stripped.startswith("{") or stripped.startswith("["):
                return FormatDetectionResult("rdf", "json-ld")
            if "rdf:RDF" in stripped or "<rdf:RDF" in stripped:
                return FormatDetectionResult("rdf", "xml")
            if stripped.startswith("<") and stripped.endswith(">"):
                return FormatDetectionResult("rdf", "turtle")
            if "," in stripped:
                return FormatDetectionResult("csv")
            break

    return FormatDetectionResult("dlgpe")
