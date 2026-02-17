import unittest

from prototyping_inference_engine.api.data.storage.rdbms.drivers import (
    HSQLDBDriver,
    MySQLDriver,
    PostgreSQLDriver,
    SQLiteDriver,
)
from prototyping_inference_engine.api.data.storage.builder import StorageBuilder


class TestRDBMSDrivers(unittest.TestCase):
    def test_sqlite_driver_connects(self):
        driver = SQLiteDriver.from_path(":memory:")
        conn = driver.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            row = cur.fetchone()
            self.assertEqual(row[0], 1)
        finally:
            conn.close()

    def test_postgresql_driver_factory(self):
        driver = PostgreSQLDriver.from_dsn("postgresql://user:pass@localhost:5432/db")
        self.assertEqual(driver.name, "postgresql")

    def test_mysql_driver_factory(self):
        driver = MySQLDriver.from_params(
            host="localhost",
            port=3306,
            user="user",
            password="pass",
            database="db",
        )
        self.assertEqual(driver.name, "mysql")

    def test_hsqldb_driver_factory(self):
        driver = HSQLDBDriver.from_jdbc("jdbc:hsqldb:mem:mymemdb")
        self.assertEqual(driver.name, "hsqldb")

    def test_builder_sets_all_rdbms_drivers(self):
        b1 = StorageBuilder.default_builder().use_postgresql_db(
            "postgresql://user:pass@localhost:5432/db"
        )
        self.assertEqual(b1._rdbms_driver.name, "postgresql")

        b2 = StorageBuilder.default_builder().use_mysql_db(
            host="localhost",
            port=3306,
            user="user",
            password="pass",
            database="db",
        )
        self.assertEqual(b2._rdbms_driver.name, "mysql")

        b3 = StorageBuilder.default_builder().use_hsqldb("jdbc:hsqldb:mem:mymemdb")
        self.assertEqual(b3._rdbms_driver.name, "hsqldb")
