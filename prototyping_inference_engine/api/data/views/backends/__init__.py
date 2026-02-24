"""Backends for view runtime sources."""

from prototyping_inference_engine.api.data.views.backends.json_web_api import (
    JSONWebAPIViewBackend,
)
from prototyping_inference_engine.api.data.views.backends.mongodb import (
    MongoDBViewBackend,
)
from prototyping_inference_engine.api.data.views.backends.sparql import (
    SparqlEndpointViewBackend,
)
from prototyping_inference_engine.api.data.views.backends.sql import SQLViewBackend

__all__ = [
    "JSONWebAPIViewBackend",
    "MongoDBViewBackend",
    "SparqlEndpointViewBackend",
    "SQLViewBackend",
]
