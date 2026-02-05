import unittest

from prototyping_inference_engine.io import DlgpeWriter
from prototyping_inference_engine.session.reasoning_session import ReasoningSession


class TestDlgpeWriter(unittest.TestCase):
    def test_writer_outputs_base_and_prefix(self) -> None:
        text = """
            @base <http://example.org/base/>.
            @prefix ex: <http://example.org/ns/>.
            <rel>(ex:obj).
        """
        session = ReasoningSession.create()
        result = session.parse(text)
        writer = DlgpeWriter()
        output = writer.write(result)

        self.assertIn("@base <http://example.org/base/>.", output)
        self.assertIn("@prefix ex: <http://example.org/ns/>.", output)
        self.assertIn("<rel>(ex:obj).", output)


if __name__ == "__main__":
    unittest.main()
