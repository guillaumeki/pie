import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from prototyping_inference_engine.api.atom.predicate import Predicate
from prototyping_inference_engine.api.atom.term.constant import Constant
from prototyping_inference_engine.api.atom.term.literal import Literal
from prototyping_inference_engine.api.atom.term.variable import Variable
from prototyping_inference_engine.api.data.basic_query import BasicQuery
from prototyping_inference_engine.api.data.views.builder import load_view_sources


class TestViewBuilderSQLite(unittest.TestCase):
    def test_load_and_evaluate_sqlite_view_with_alias(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            db_path = base / "people.db"
            vd_path = base / "people.vd"

            connection = sqlite3.connect(db_path)
            try:
                connection.execute(
                    "CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT)"
                )
                connection.execute("INSERT INTO people(id, name) VALUES (1, 'Alice')")
                connection.execute("INSERT INTO people(id, name) VALUES (2, 'Bob')")
                connection.commit()
            finally:
                connection.close()

            document = {
                "datasources": [
                    {
                        "id": "main",
                        "protocol": "SQLite",
                        "parameters": {"url": "people.db"},
                    }
                ],
                "views": [
                    {
                        "id": "personById",
                        "datasource": "main",
                        "query": "SELECT name FROM people WHERE id = %%id%%",
                        "signature": [{"mandatory": "%%id%%"}, {}],
                    }
                ],
            }
            vd_path.write_text(json.dumps(document), encoding="utf-8")

            sources = load_view_sources(vd_path, alias_prefix="v")
            self.assertEqual(len(sources), 1)
            source = sources[0]

            predicate = Predicate("v:personById", 2)
            query = BasicQuery(
                predicate=predicate,
                bound_positions={0: Constant("1")},
                answer_variables={1: Variable("X")},
            )

            self.assertTrue(source.can_evaluate(query))
            answers = list(source.evaluate(query))
            self.assertEqual(len(answers), 1)
            self.assertEqual(len(answers[0]), 1)
            self.assertIsInstance(answers[0][0], Literal)
            self.assertEqual(answers[0][0].identifier, "Alice")

    def test_mandatory_binding_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            db_path = base / "people.db"
            vd_path = base / "people.vd"

            connection = sqlite3.connect(db_path)
            try:
                connection.execute(
                    "CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT)"
                )
                connection.execute("INSERT INTO people(id, name) VALUES (1, 'Alice')")
                connection.commit()
            finally:
                connection.close()

            document = {
                "datasources": [
                    {
                        "id": "main",
                        "protocol": "SQLite",
                        "parameters": {"url": "people.db"},
                    }
                ],
                "views": [
                    {
                        "id": "personById",
                        "datasource": "main",
                        "query": "SELECT name FROM people WHERE id = %%id%%",
                        "signature": [{"mandatory": "%%id%%"}, {}],
                    }
                ],
            }
            vd_path.write_text(json.dumps(document), encoding="utf-8")

            source = load_view_sources(vd_path, alias_prefix="v")[0]
            predicate = Predicate("v:personById", 2)
            query = BasicQuery(
                predicate=predicate,
                bound_positions={},
                answer_variables={1: Variable("X")},
            )

            self.assertFalse(source.can_evaluate(query))
            with self.assertRaises(ValueError):
                list(source.evaluate(query))


if __name__ == "__main__":
    unittest.main()
