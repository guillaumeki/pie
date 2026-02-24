"""MongoDB backend for declared views."""

from __future__ import annotations

import json
from typing import Any

from prototyping_inference_engine.api.data.views.source import (
    CompiledView,
    ViewQueryBackend,
)
from prototyping_inference_engine.api.data.views.specialization import (
    SpecializedViewInvocation,
)


class MongoDBViewBackend(ViewQueryBackend):
    """Execute MongoDB aggregation pipelines for declared views."""

    def __init__(self, url: str, database: str, collection: str):
        self._url = url
        self._database = database
        self._collection = collection

    def fetch_rows(
        self,
        compiled_view: CompiledView,
        invocation: SpecializedViewInvocation,
    ):
        try:
            from pymongo import MongoClient  # type: ignore[import-not-found,import-untyped]
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("pymongo is required for MongoDB view backends") from exc

        query_object = json.loads(invocation.query_text)
        if isinstance(query_object, list):
            pipeline = query_object
        else:
            pipeline = [query_object]

        client = MongoClient(self._url)
        try:
            collection = client[self._database][self._collection]
            cursor = collection.aggregate(pipeline)
            for document in cursor:
                projected: list[object | None] = []
                for position in compiled_view.non_mandatory_positions:
                    selection = invocation.selections[position]
                    projected.append(_select_from_document(document, selection))
                yield tuple(projected)
        finally:
            client.close()


def _select_from_document(
    document: dict[str, Any], selection: str | None
) -> object | None:
    if selection is None:
        return None

    normalized = selection
    if normalized.startswith("$"):
        normalized = normalized[1:]
    if normalized.startswith("."):
        normalized = normalized[1:]
    if not normalized:
        return document

    current: object = document
    for key in normalized.split("."):
        if not isinstance(current, dict):
            return None
        if key not in current:
            return None
        current = current[key]
    return current
