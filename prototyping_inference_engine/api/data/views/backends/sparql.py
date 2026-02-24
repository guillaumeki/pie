"""SPARQL endpoint backend for declared views."""

from __future__ import annotations

import base64
import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from prototyping_inference_engine.api.data.views.source import (
    CompiledView,
    ViewQueryBackend,
)
from prototyping_inference_engine.api.data.views.specialization import (
    SpecializedViewInvocation,
)


class SparqlEndpointViewBackend(ViewQueryBackend):
    """Execute SPARQL SELECT queries against an HTTP endpoint."""

    def __init__(
        self,
        endpoint_url: str,
        *,
        user: str | None = None,
        password: str | None = None,
    ):
        self._endpoint_url = endpoint_url
        self._user = user
        self._password = password

    def fetch_rows(
        self,
        compiled_view: CompiledView,
        invocation: SpecializedViewInvocation,
    ):
        params = urlencode(
            {
                "query": invocation.query_text,
                "format": "application/sparql-results+json",
            }
        )
        separator = "&" if "?" in self._endpoint_url else "?"
        request = Request(self._endpoint_url + separator + params)

        if self._user is not None and self._password is not None:
            token = f"{self._user}:{self._password}".encode("utf-8")
            encoded = base64.b64encode(token).decode("ascii")
            request.add_header("Authorization", f"Basic {encoded}")

        with urlopen(request) as response:  # nosec B310
            payload = response.read().decode("utf-8")

        parsed = json.loads(payload)
        variables: list[str] = parsed.get("head", {}).get("vars", [])
        bindings: list[dict[str, Any]] = parsed.get("results", {}).get("bindings", [])

        expected = len(compiled_view.non_mandatory_positions)
        for binding in bindings:
            values: list[object | None] = []
            for variable in variables:
                values.append(_binding_to_python(binding.get(variable)))
            if len(values) < expected:
                values.extend([None] * (expected - len(values)))
            yield tuple(values[:expected])


def _binding_to_python(entry: dict[str, Any] | None) -> object | None:
    if not entry:
        return None

    kind = entry.get("type")
    value = entry.get("value")
    if value is None:
        return None

    if kind == "bnode":
        return f"_:{value}"

    if kind == "literal":
        datatype = str(entry.get("datatype") or "")
        lexical = str(value)
        if datatype.endswith("#integer"):
            try:
                return int(lexical)
            except ValueError:
                return lexical
        if datatype.endswith("#decimal") or datatype.endswith("#double"):
            try:
                return float(lexical)
            except ValueError:
                return lexical
        if datatype.endswith("#boolean"):
            return lexical.lower() == "true"
        return lexical

    return str(value)
