import tempfile
import unittest
from pathlib import Path

from prototyping_inference_engine.api.data.views.builder import (
    load_view_sources_from_document,
)
from prototyping_inference_engine.api.data.views.errors import ViewValidationError
from prototyping_inference_engine.api.data.views.model import (
    DatasourceDeclaration,
    ViewAttributeSpec,
    ViewDeclaration,
    ViewDocument,
)


class TestViewValidation(unittest.TestCase):
    def test_duplicate_datasource_identifier_raises(self):
        document = ViewDocument(
            datasources=(
                DatasourceDeclaration(
                    id="d", protocol="SQLite", parameters={"url": ":memory:"}
                ),
                DatasourceDeclaration(
                    id="d", protocol="SQLite", parameters={"url": ":memory:"}
                ),
            ),
            views=(
                ViewDeclaration(
                    id="v",
                    datasource="d",
                    signature=(ViewAttributeSpec(),),
                    query="SELECT 1",
                ),
            ),
        )

        with self.assertRaises(ViewValidationError):
            load_view_sources_from_document(document)

    def test_view_with_unknown_datasource_raises(self):
        document = ViewDocument(
            datasources=(
                DatasourceDeclaration(
                    id="d", protocol="SQLite", parameters={"url": ":memory:"}
                ),
            ),
            views=(
                ViewDeclaration(
                    id="v",
                    datasource="missing",
                    signature=(ViewAttributeSpec(),),
                    query="SELECT 1",
                ),
            ),
        )

        with self.assertRaises(ViewValidationError):
            load_view_sources_from_document(document)

    def test_query_file_must_exist(self):
        document = ViewDocument(
            datasources=(
                DatasourceDeclaration(
                    id="d", protocol="SQLite", parameters={"url": ":memory:"}
                ),
            ),
            views=(
                ViewDeclaration(
                    id="v",
                    datasource="d",
                    signature=(ViewAttributeSpec(),),
                    query_file="missing.sql",
                ),
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ViewValidationError):
                load_view_sources_from_document(document, base_dir=Path(tmpdir))


if __name__ == "__main__":
    unittest.main()
