import tempfile
import unittest
from pathlib import Path
import sqlite3

from prototyping_inference_engine.rdf.translator import RDFTranslationMode
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestImportResolution(unittest.TestCase):
    def test_imports_csv_and_rdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            csv_path = base / "facts.csv"
            csv_path.write_text("a,b\n", encoding="utf-8")

            rdf_path = base / "data.ttl"
            rdf_path.write_text(
                """
                @prefix ex: <http://example.org/> .
                ex:a ex:knows ex:b .
                """,
                encoding="utf-8",
            )

            dlgpe_path = base / "main.dlgpe"
            dlgpe_path.write_text(
                """
                @import <facts.csv>.
                @import <data.ttl>.

                @facts
                p(a).
                """,
                encoding="utf-8",
            )

            session = ReasoningSession.create(
                rdf_translation_mode=RDFTranslationMode.RAW
            )
            result = session.parse_file(dlgpe_path)

            predicates = {atom.predicate.name for atom in result.facts}
            self.assertIn("p", predicates)
            self.assertIn("facts", predicates)
            self.assertIn("triple", predicates)

    def test_import_vd_adds_view_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            db_path = base / "people.db"
            vd_path = base / "views.vd"
            main_path = base / "main.dlgpe"

            connection = sqlite3.connect(db_path)
            try:
                connection.execute("CREATE TABLE people (name TEXT)")
                connection.execute("INSERT INTO people(name) VALUES ('alice')")
                connection.execute("INSERT INTO people(name) VALUES ('bob')")
                connection.commit()
            finally:
                connection.close()

            vd_path.write_text(
                (
                    "{"
                    '"datasources":[{"id":"db","protocol":"SQLite",'
                    '"parameters":{"url":"people.db"}}],'
                    '"views":[{"id":"people","datasource":"db",'
                    '"query":"SELECT name FROM people","signature":[{}]}]'
                    "}"
                ),
                encoding="utf-8",
            )

            main_path.write_text(
                """
                @import <views.vd>.
                ?(X) :- people(X).
                """,
                encoding="utf-8",
            )

            with ReasoningSession.create() as session:
                result = session.parse_file(main_path)
                fact_base = session.create_fact_base(result.facts)
                answers = list(
                    session.evaluate_query_with_sources(
                        result.queries[0], fact_base, result.sources
                    )
                )

            values = sorted(answer[0].identifier for answer in answers)
            self.assertEqual(values, ["alice", "bob"])

    def test_view_directive_loads_aliased_views(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            db_path = base / "people.db"
            vd_path = base / "views.vd"
            main_path = base / "main.dlgpe"

            connection = sqlite3.connect(db_path)
            try:
                connection.execute("CREATE TABLE people (name TEXT)")
                connection.execute("INSERT INTO people(name) VALUES ('alice')")
                connection.execute("INSERT INTO people(name) VALUES ('bob')")
                connection.commit()
            finally:
                connection.close()

            vd_path.write_text(
                (
                    "{"
                    '"datasources":[{"id":"db","protocol":"SQLite",'
                    '"parameters":{"url":"people.db"}}],'
                    '"views":[{"id":"people","datasource":"db",'
                    '"query":"SELECT name FROM people","signature":[{}]}]'
                    "}"
                ),
                encoding="utf-8",
            )

            main_path.write_text(
                """
                @view v:<views.vd>
                ?(X) :- v:people(X).
                """,
                encoding="utf-8",
            )

            with ReasoningSession.create() as session:
                result = session.parse_file(main_path)
                fact_base = session.create_fact_base(result.facts)
                answers = list(
                    session.evaluate_query_with_sources(
                        result.queries[0], fact_base, result.sources
                    )
                )

            values = sorted(answer[0].identifier for answer in answers)
            self.assertEqual(values, ["alice", "bob"])
