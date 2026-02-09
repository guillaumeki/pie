import json
from pathlib import Path
import tempfile
import unittest

from prototyping_inference_engine.api.atom.term.factory.literal_factory import (
    LiteralFactory,
)
from prototyping_inference_engine.api.atom.term.storage.dict_storage import DictStorage
from prototyping_inference_engine.api.data.python_function_data import (
    PythonFunctionReadable,
)
from prototyping_inference_engine.io.parsers.dlgpe.computed_function_loader import (
    load_computed_config,
    register_python_functions,
)


class TestComputedFunctionLoader(unittest.TestCase):
    def test_registers_functions_from_legacy_block(self) -> None:
        resource_dir = Path(__file__).resolve().parent / "resources"
        config_path = resource_dir / "functions.json"

        config = load_computed_config(config_path)
        source = PythonFunctionReadable(LiteralFactory(DictStorage()))
        registered = register_python_functions("ex", config, source)

        self.assertIn("ex:increment", registered)
        self.assertIn("ex:increment", source.function_names())

    def test_rejects_invalid_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "bad.json"
            config_path.write_text(json.dumps({"schema_version": 0}), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_computed_config(config_path)


if __name__ == "__main__":
    unittest.main()
