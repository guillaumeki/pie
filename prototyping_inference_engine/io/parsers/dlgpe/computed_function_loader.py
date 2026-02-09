"""
Load computed function configurations from JSON files.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import inspect
import json
from pathlib import Path
import sys
from typing import Callable, Iterable, Optional, cast

from prototyping_inference_engine.api.data.python_function_data import (
    PythonFunctionReadable,
)


@dataclass(frozen=True)
class PythonFunctionProvider:
    module: str
    class_name: Optional[str]
    search_path: Path


@dataclass(frozen=True)
class ComputedProviderConfig:
    python: tuple[PythonFunctionProvider, ...]


def load_computed_config(path: Path) -> ComputedProviderConfig:
    path = path.resolve()
    if not path.exists():
        raise ValueError(f"Computed configuration file not found: {path}")
    if path.suffix.lower() != ".json":
        raise ValueError(f"Computed configuration must be a .json file: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Computed configuration must be a JSON object")

    schema_version = data.get("schema_version")
    if schema_version is not None:
        if not isinstance(schema_version, int) or schema_version < 1:
            raise ValueError("schema_version must be a positive integer")
        if schema_version != 1:
            raise ValueError(f"Unsupported schema_version: {schema_version}")

    default = data.get("default", {})
    if not isinstance(default, dict):
        raise ValueError("default section must be a JSON object")

    python_providers: list[PythonFunctionProvider] = []

    legacy_functions = default.get("functions")
    if legacy_functions is not None:
        python_providers.append(_parse_python_provider(legacy_functions, path.parent))

    providers = default.get("providers", {})
    if providers is not None:
        if not isinstance(providers, dict):
            raise ValueError("providers section must be a JSON object")
        python_entry = providers.get("python")
        if python_entry is not None:
            python_providers.extend(
                _parse_python_provider_entries(python_entry, path.parent)
            )

    if not python_providers:
        raise ValueError("No supported computed providers found in configuration")

    return ComputedProviderConfig(python=tuple(python_providers))


def register_python_functions(
    prefix: str, config: ComputedProviderConfig, source: PythonFunctionReadable
) -> set[str]:
    registered: set[str] = set()
    for provider in config.python:
        module = _import_module(provider.module, provider.search_path)
        target = module
        if provider.class_name:
            if not hasattr(module, provider.class_name):
                raise ValueError(
                    f"Computed class '{provider.class_name}' not found in module "
                    f"'{provider.module}'"
                )
            target = getattr(module, provider.class_name)

        for name, func in _iter_public_callables(target):
            qualified = f"{prefix}:{name}"
            source.register_function(
                qualified, cast(Callable[..., object], func), mode="python"
            )
            registered.add(qualified)
    return registered


def _parse_python_provider_entries(
    entry: object, base_dir: Path
) -> Iterable[PythonFunctionProvider]:
    if isinstance(entry, list):
        for item in entry:
            yield _parse_python_provider(item, base_dir)
        return
    yield _parse_python_provider(entry, base_dir)


def _parse_python_provider(entry: object, base_dir: Path) -> PythonFunctionProvider:
    if not isinstance(entry, dict):
        raise ValueError("Python provider must be a JSON object")
    raw_path = entry.get("path", ".")
    if not isinstance(raw_path, str):
        raise ValueError("Python provider path must be a string")
    module = entry.get("module") or entry.get("package")
    if not isinstance(module, str) or not module:
        raise ValueError("Python provider must define a module or package")
    class_name = entry.get("class")
    if class_name is not None and not isinstance(class_name, str):
        raise ValueError("Python provider class must be a string")

    search_path = (base_dir / raw_path).resolve()
    if not search_path.exists():
        raise ValueError(f"Python provider path does not exist: {search_path}")
    if not search_path.is_dir():
        raise ValueError(f"Python provider path is not a directory: {search_path}")

    return PythonFunctionProvider(
        module=module, class_name=class_name, search_path=search_path
    )


def _import_module(module: str, search_path: Path):
    search_path_str = str(search_path)
    sys.path.insert(0, search_path_str)
    try:
        importlib.invalidate_caches()
        return importlib.import_module(module)
    finally:
        if sys.path and sys.path[0] == search_path_str:
            sys.path.pop(0)


def _iter_public_callables(target) -> Iterable[tuple[str, Callable[..., object]]]:
    for name, value in inspect.getmembers(target):
        if name.startswith("_"):
            continue
        if inspect.isfunction(value) or inspect.ismethod(value):
            yield name, value
