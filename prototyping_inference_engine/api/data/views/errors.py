"""View declaration and runtime errors."""

from __future__ import annotations


class ViewError(ValueError):
    """Base class for view-related errors."""


class ViewParseError(ViewError):
    """Raised when a view declaration document cannot be parsed."""


class ViewValidationError(ViewError):
    """Raised when a view declaration document violates semantic constraints."""


class ViewLoadingError(ViewError):
    """Raised when a view declaration cannot be loaded into runtime sources."""


class MissingMandatoryBindingError(ViewError):
    """Raised when a mandatory view parameter has no bound value."""


class UnsupportedDatasourceProtocolError(ViewLoadingError):
    """Raised when a datasource protocol is unknown at runtime."""
