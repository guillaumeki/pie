"""JSON Web API backend for declared views."""

from __future__ import annotations

import base64
import json
from typing import Any
from urllib.request import Request, urlopen

from prototyping_inference_engine.api.data.views.source import (
    CompiledView,
    ViewQueryBackend,
)
from prototyping_inference_engine.api.data.views.specialization import (
    SpecializedViewInvocation,
)

try:  # pragma: no cover - optional dependency
    from jsonpath_ng.ext import (  # type: ignore[import-not-found,import-untyped]
        parse as parse_jsonpath,
    )
except Exception:  # pragma: no cover - optional dependency
    parse_jsonpath = None


class JSONWebAPIViewBackend(ViewQueryBackend):
    """Execute view queries as HTTP GET requests returning JSON documents."""

    def __init__(
        self,
        *,
        user: str | None = None,
        password: str | None = None,
    ):
        self._user = user
        self._password = password

    def fetch_rows(
        self,
        compiled_view: CompiledView,
        invocation: SpecializedViewInvocation,
    ):
        request = Request(invocation.query_text)
        if self._user is not None and self._password is not None:
            token = f"{self._user}:{self._password}".encode("utf-8")
            encoded = base64.b64encode(token).decode("ascii")
            request.add_header("Authorization", f"Basic {encoded}")

        with urlopen(request) as response:  # nosec B310
            payload = response.read().decode("utf-8")

        document = json.loads(payload)
        position = invocation.position or "$"
        nodes = jsonpath_values(document, position)

        non_mandatory_positions = compiled_view.non_mandatory_positions
        for node in nodes:
            projected: list[object | None] = []
            for position_index in non_mandatory_positions:
                selection = invocation.selections[position_index]
                if selection is None:
                    projected.append(node)
                    continue
                values = jsonpath_values(node, selection)
                projected.append(values[0] if values else None)
            yield tuple(projected)


def jsonpath_values(document: Any, expression: str) -> list[Any]:
    """Evaluate a JSONPath expression with an optional stdlib fallback."""
    if parse_jsonpath is not None:
        return [match.value for match in parse_jsonpath(expression).find(document)]
    return _simple_jsonpath_values(document, expression)


def _simple_jsonpath_values(document: Any, expression: str) -> list[Any]:
    if expression == "$":
        return [document]

    if not expression.startswith("$"):
        raise ValueError(f"Unsupported JSONPath expression: {expression}")

    tokens = _tokenize_simple_jsonpath(expression)
    current = [document]

    for token in tokens:
        next_values: list[Any] = []
        if token == "*":
            for value in current:
                if isinstance(value, list):
                    next_values.extend(value)
                elif isinstance(value, dict):
                    next_values.extend(value.values())
            current = next_values
            continue

        if isinstance(token, int):
            for value in current:
                if isinstance(value, list) and 0 <= token < len(value):
                    next_values.append(value[token])
            current = next_values
            continue

        for value in current:
            if isinstance(value, dict) and token in value:
                next_values.append(value[token])
        current = next_values

    return current


def _tokenize_simple_jsonpath(expression: str) -> list[str | int]:
    if expression == "$":
        return []

    rest = expression[1:]
    if rest.startswith("."):
        rest = rest[1:]

    tokens: list[str | int] = []
    for chunk in rest.split("."):
        if not chunk:
            continue

        while "[" in chunk and chunk.endswith("]"):
            name, _, selector = chunk.partition("[")
            selector = selector[:-1]
            if name:
                tokens.append(name)
            if selector == "*":
                tokens.append("*")
            else:
                tokens.append(int(selector))
            chunk = ""

        if chunk:
            tokens.append(chunk)

    return tokens
