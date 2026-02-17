"""Tests for MutableMaterializedCoreProcessor."""

import unittest

from prototyping_inference_engine.api.atom.set.core.naive_core_processor import (
    NaiveCoreProcessor,
)
from prototyping_inference_engine.api.fact_base.core.fact_base_core_processor import (
    MutableMaterializedCoreProcessor,
)
from prototyping_inference_engine.api.fact_base.mutable_in_memory_fact_base import (
    MutableInMemoryFactBase,
)
from prototyping_inference_engine.io.parsers.dlgpe import DlgpeParser


class TestMutableMaterializedCoreProcessor(unittest.TestCase):
    def test_compute_core_in_place(self) -> None:
        parser = DlgpeParser.instance()
        fb = MutableInMemoryFactBase(
            parser.parse_atoms(
                "r(X), t(X,a,b), s(a,z), r(Y), t(Y,a,b), relatedTo(Y,z)."
            )
        )

        processor = MutableMaterializedCoreProcessor(NaiveCoreProcessor.instance())
        processor.compute_core(fb)

        self.assertLess(len(fb), 6)


if __name__ == "__main__":
    unittest.main()
