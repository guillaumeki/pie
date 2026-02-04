"""
Term storage strategies for caching and memory management.

This package provides different strategies for storing terms:
- DictStorage: Simple dictionary, no auto-cleanup
- WeakRefStorage: Weak references, auto-cleanup via GC
- GlobalCacheStorage: Delegates to existing global caches
"""

from prototyping_inference_engine.api.atom.term.storage.storage_strategy import (
    TermStorageStrategy,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import (
    DictStorage,
)
from prototyping_inference_engine.api.atom.term.storage.weak_ref_storage import (
    WeakRefStorage,
)
from prototyping_inference_engine.api.atom.term.storage.global_cache_storage import (
    GlobalCacheStorage,
)

__all__ = [
    "TermStorageStrategy",
    "DictStorage",
    "WeakRefStorage",
    "GlobalCacheStorage",
]
