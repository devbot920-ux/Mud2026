import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inventory_sources.py"
SPEC = importlib.util.spec_from_file_location("inventory_sources", SCRIPT)
inventory = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(inventory)


class InventorySourcesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.input_dir = self.root / "inputs"
        self.input_dir.mkdir()
        (self.input_dir / "b.dat").write_bytes(b"second")
        (self.input_dir / "a.dat").write_bytes(b"first")
        (self.input_dir / "ignored.txt").write_text("ignored", encoding="utf-8")
        self.config = self.root / "sources.json"
        self.config.write_text(
            json.dumps(
                {
                    "sources": [
                        {
                            "name": "fixture",
                            "path": str(self.input_dir),
                            "include": ["*.dat", "a.dat"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_hash_is_sha256(self):
        self.assertEqual(
            inventory.sha256_file(self.input_dir / "a.dat"),
            "a7937b64b8caa58f03721bb6bacf5c78cb235febe0e70b1b84cd99541461a08e",
        )

    def test_discovery_is_sorted_and_deduplicated(self):
        config = json.loads(self.config.read_text(encoding="utf-8"))
        found = inventory.discover_sources(config)
        self.assertEqual([path.name for _, path in found], ["a.dat", "b.dat"])

    def test_manifest_contains_metadata_without_changing_inputs(self):
        before = {path.name: path.read_bytes() for path in self.input_dir.iterdir()}
        manifest = inventory.build_manifest(self.config)
        after = {path.name: path.read_bytes() for path in self.input_dir.iterdir()}

        self.assertEqual(before, after)
        self.assertEqual(manifest["file_count"], 2)
        self.assertEqual(manifest["total_size_bytes"], 11)
        self.assertEqual(manifest["hash_algorithm"], "sha256")
        self.assertEqual(
            set(manifest["files"][0]),
            {"source", "path", "size_bytes", "modified_utc", "sha256"},
        )

    def test_write_manifest_creates_only_output_tree(self):
        output = self.root / "result" / "manifest.json"
        manifest = inventory.build_manifest(self.config)
        inventory.write_manifest(manifest, output)
        loaded = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(loaded["file_count"], 2)
        self.assertTrue(output.read_bytes().endswith(b"\n"))

    def test_manifest_output_is_deterministic(self):
        first = self.root / "first.json"
        second = self.root / "second.json"
        inventory.write_manifest(inventory.build_manifest(self.config), first)
        inventory.write_manifest(inventory.build_manifest(self.config), second)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_missing_source_fails(self):
        with self.assertRaises(FileNotFoundError):
            inventory.discover_sources(
                {"sources": [{"name": "missing", "path": str(self.root / "none")}]}
            )


if __name__ == "__main__":
    unittest.main()
