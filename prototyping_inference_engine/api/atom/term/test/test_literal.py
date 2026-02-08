import unittest
from datetime import datetime, time, timezone
from decimal import Decimal

from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.literal_config import (
    LiteralConfig,
    LiteralNormalization,
    LiteralComparison,
)
from prototyping_inference_engine.api.atom.term.literal_xsd import (
    XsdDuration,
    XsdGYear,
    XsdGYearMonth,
    XsdGMonthDay,
    XsdGDay,
    XsdGMonth,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage


class TestLiteralFactoryDefaults(unittest.TestCase):
    def test_normalized_integer(self):
        factory = LiteralFactory(DictStorage(), LiteralConfig.default())
        lit = factory.create("01", "xsd:integer")
        self.assertEqual(lit.value, 1)
        self.assertEqual(lit.lexical, "1")
        self.assertEqual(lit.datatype, "xsd:integer")

    def test_language_literal(self):
        factory = LiteralFactory(DictStorage(), LiteralConfig.default())
        lit = factory.create("chat", lang="fr")
        self.assertEqual(lit.lang, "fr")
        self.assertEqual(lit.lexical, "chat")


class TestLiteralFactoryConfig(unittest.TestCase):
    def test_raw_lexical_comparison(self):
        config = LiteralConfig(
            normalization=LiteralNormalization.RAW_LEXICAL,
            comparison=LiteralComparison.BY_LEXICAL,
            keep_lexical=False,
        )
        factory = LiteralFactory(DictStorage(), config)
        lit = factory.create("01", "xsd:integer")
        self.assertEqual(lit.value, "01")
        self.assertIsNone(lit.lexical)
        self.assertEqual(lit.comparison_key, ("xsd:integer", "01", None))
        self.assertEqual(lit.datatype, "xsd:integer")


class TestLiteralFactoryXsdAdvanced(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = LiteralFactory(DictStorage(), LiteralConfig.default())

    def test_datetime_normalization(self):
        lit = self.factory.create("2024-06-01T12:34:56Z", "xsd:dateTime")
        self.assertEqual(
            lit.value, datetime(2024, 6, 1, 12, 34, 56, tzinfo=timezone.utc)
        )
        self.assertEqual(lit.lexical, "2024-06-01T12:34:56Z")
        self.assertEqual(lit.datatype, "xsd:dateTime")

    def test_time_with_timezone(self):
        lit = self.factory.create("12:34:56+02:00", "xsd:time")
        self.assertEqual(lit.value, time.fromisoformat("12:34:56+02:00"))
        self.assertEqual(lit.lexical, "12:34:56+02:00")
        self.assertEqual(lit.datatype, "xsd:time")

    def test_date_normalization(self):
        lit = self.factory.create("2024-06-01", "xsd:date")
        self.assertEqual(lit.value, datetime(2024, 6, 1).date())
        self.assertEqual(lit.datatype, "xsd:date")

    def test_duration_normalization(self):
        lit = self.factory.create("P1Y2M3DT4H5M6.7S", "xsd:duration")
        self.assertEqual(
            lit.value,
            XsdDuration(1, 1, 2, 3, 4, 5, Decimal("6.7")),
        )
        self.assertEqual(lit.lexical, "P1Y2M3DT4H5M6.7S")
        self.assertEqual(lit.datatype, "xsd:duration")

    def test_g_year_g_month_variants(self):
        gyear = self.factory.create("2024Z", "xsd:gYear")
        gyear_month = self.factory.create("2024-06Z", "xsd:gYearMonth")
        gmonth_day = self.factory.create("--12-25", "xsd:gMonthDay")
        gday = self.factory.create("---15", "xsd:gDay")
        gmonth = self.factory.create("--08", "xsd:gMonth")
        self.assertEqual(gyear.value, XsdGYear(2024, "Z"))
        self.assertEqual(gyear_month.value, XsdGYearMonth(2024, 6, "Z"))
        self.assertEqual(gmonth_day.value, XsdGMonthDay(12, 25, None))
        self.assertEqual(gday.value, XsdGDay(15, None))
        self.assertEqual(gmonth.value, XsdGMonth(8, None))
        self.assertEqual(gyear.lexical, "2024Z")

    def test_binary_normalization(self):
        base64_lit = self.factory.create("aGVsbG8=", "xsd:base64Binary")
        hex_lit = self.factory.create("0A0B", "xsd:hexBinary")
        self.assertEqual(base64_lit.value, b"hello")
        self.assertEqual(base64_lit.lexical, "aGVsbG8=")
        self.assertEqual(hex_lit.value, b"\x0a\x0b")
        self.assertEqual(hex_lit.lexical, "0a0b")

    def test_qname_and_multivalue_strings(self):
        qname = self.factory.create("ex:local", "xsd:QName")
        tokens = self.factory.create("a b c", "xsd:NMTOKENS")
        self.assertEqual(qname.value, ("ex", "local"))
        self.assertEqual(qname.lexical, "ex:local")
        self.assertEqual(tokens.value, ("a", "b", "c"))
        self.assertEqual(tokens.lexical, "a b c")
