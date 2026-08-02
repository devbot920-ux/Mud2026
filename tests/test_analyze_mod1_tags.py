import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_mod1_tags import analyze, dll_calls, read_mod1, render_markdown


class Mod1TagAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def baseline(self):
        path = self.root / "baseline.sqlite"
        c = sqlite3.connect(path)
        c.executescript("""
          CREATE TABLE source_file(source_file_id INTEGER, logical_name TEXT);
          CREATE TABLE source_row(source_row_id INTEGER, source_file_id INTEGER, table_name TEXT);
          CREATE TABLE source_value(source_row_id INTEGER, column_name TEXT, integer_value INTEGER, blob_value BLOB);
          INSERT INTO source_file VALUES(1,'RCI_MOD1');
          INSERT INTO source_row VALUES(1,1,'data_t'),(2,1,'data_t'),(3,1,'data_t');
          INSERT INTO source_value VALUES(1,'key_0',7,NULL),(1,'key_1',1,NULL),(1,'data',NULL,X'00000000000000000A01');
          INSERT INTO source_value VALUES(2,'key_0',7,NULL),(2,'key_1',2,NULL),(2,'data',NULL,X'0000000000000000E401');
          INSERT INTO source_value VALUES(3,'key_0',8,NULL),(3,'key_1',1,NULL),(3,'data',NULL,X'0000000000000000E402');
        """)
        c.commit(); c.close()
        return path

    def test_read_only_load_and_association(self):
        path = self.baseline(); before = path.stat().st_mtime_ns
        rows = read_mod1(path)
        catalog = analyze(rows, {})
        limited = next(x for x in catalog if x["tag"] == "0xE4")
        self.assertEqual(limited["record_count"], 2)
        self.assertEqual(limited["entity_key_associations"], {"room": 1, "unanchored": 1})
        self.assertEqual(limited["variable_offsets"], [9])
        self.assertEqual(path.stat().st_mtime_ns, before)

    def test_dll_parser_tracks_real_function_and_line(self):
        path = self.root / "x.c"
        path.write_text("int _SHOP(void)\n{\n  x = _ACQUIRE_MODIFICATION(p,0xe4);\n}\n", encoding="utf-8")
        calls = dll_calls(path)
        self.assertEqual(calls[0xE4], [{"function":"_SHOP", "line":3}])

    def test_markdown_excludes_bytes_and_source_text(self):
        catalog = analyze(read_mod1(self.baseline()), {})
        report = {"counts":{"records":3,"tags":len(catalog),"interpreted":2,"unresolved":0}, "catalog":catalog, "ranked_unresolved_tags":[]}
        markdown = render_markdown(report)
        self.assertNotIn("00000000", markdown)
        self.assertIn("Phase 3", markdown)


if __name__ == "__main__":
    unittest.main()
