"""Regression tests for Mermaid staging-only transformation."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_mermaid.py"
SPEC = importlib.util.spec_from_file_location("render_mermaid", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
mermaid = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mermaid)

# Valid tiny PNG. The renderer is mocked: CLI rendering is smoke-tested in
# the published image, and the whole PDF path in a real consumer.
PNG = bytes.fromhex(
    "89504e470d0a1a0a"
    "0000000d49484452000000010000000108060000001f15c489"
    "0000000b49444154789c636000020000050001a5f64540"
    "0000000049454e44ae426082"
)


class TestMermaidRender(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "patterns.md"
        self.seen = []

    def fake_renderer(self, source, output):
        self.seen.append(source)
        output.write_bytes(PNG)

    def test_two_diagrams_and_normal_cpp_code(self):
        original = (
            "# Title\n\n"
            "```cpp\nint main() { return 0; }\n```\n\n"
            "```mermaid\nclassDiagram\n  A <|-- B\n```\n\n"
            "~~~mermaid\nflowchart LR\n  A --> B\n~~~\n"
        )
        self.path.write_text(original, encoding="utf-8")
        count = mermaid.render_markdown(self.path, self.fake_renderer)
        self.assertEqual(count, 2)
        after = self.path.read_text(encoding="utf-8")
        self.assertIn("```cpp\nint main()", after)
        self.assertIn("![Mermaid diagram 1](patterns-mermaid-001.png)", after)
        self.assertIn("![Mermaid diagram 2](patterns-mermaid-002.png)", after)
        self.assertNotIn("flowchart LR", after)
        self.assertEqual(len(self.seen), 2)
        self.assertEqual(
            (self.root / "patterns-mermaid-001.png").read_bytes(), PNG
        )

    def test_inner_mermaid_example_is_not_rendered(self):
        source = (
            "````markdown\n"
            "```mermaid\nclassDiagram\n  A <|-- B\n```\n"
            "````\n"
        )
        self.path.write_text(source, encoding="utf-8")
        self.assertEqual(mermaid.render_markdown(self.path, self.fake_renderer), 0)
        self.assertEqual(self.path.read_text(encoding="utf-8"), source)

    def test_unclosed_mermaid_fails_closed(self):
        self.path.write_text("```mermaid\nclassDiagram\n  A <|-- B\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unclosed Mermaid"):
            mermaid.render_markdown(self.path, self.fake_renderer)

    def test_failed_png_does_not_replace_source(self):
        source = "```mermaid\nclassDiagram\n  A <|-- B\n```\n"
        self.path.write_text(source, encoding="utf-8")

        def corrupt(_source, output):
            output.write_bytes(b"not a png")

        with self.assertRaisesRegex(RuntimeError, "non-PNG"):
            mermaid.render_markdown(self.path, corrupt)
        self.assertEqual(self.path.read_text(encoding="utf-8"), source)

    def test_original_is_unchanged_without_mermaid(self):
        source = "# Notes\n\n```cpp\nreturn 42;\n```\n"
        self.path.write_text(source, encoding="utf-8")
        self.assertEqual(mermaid.render_markdown(self.path, self.fake_renderer), 0)
        self.assertEqual(self.path.read_text(encoding="utf-8"), source)


if __name__ == "__main__":
    unittest.main()
