"""SQL backend for declared relational views."""

from __future__ import annotations

from contextlib import closing

from prototyping_inference_engine.api.data.storage.rdbms.drivers import RDBMSDriver
from prototyping_inference_engine.api.data.views.source import (
    CompiledView,
    ViewQueryBackend,
)
from prototyping_inference_engine.api.data.views.specialization import (
    SpecializedViewInvocation,
)


class SQLViewBackend(ViewQueryBackend):
    """Execute view queries on SQL datasources."""

    def __init__(self, driver: RDBMSDriver):
        self._driver = driver

    def fetch_rows(
        self,
        compiled_view: CompiledView,
        invocation: SpecializedViewInvocation,
    ):
        del compiled_view
        connection = self._driver.connect()
        try:
            with closing(connection.cursor()) as cursor:
                cursor.execute(invocation.query_text)
                rows = cursor.fetchall()
            for row in rows:
                if isinstance(row, tuple):
                    yield row
                elif isinstance(row, list):
                    yield tuple(row)
                else:
                    yield tuple(row)
        finally:
            connection.close()
