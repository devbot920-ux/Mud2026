import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.audit_canonical_topology import (
    build_report,
    combine_with_derived_nodes,
    read_canonical_topology,
    render_markdown,
)


class CanonicalTopologyAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def baseline(self) -> Path:
        path = self.root / "baseline.sqlite"
        connection = sqlite3.connect(path)
        connection.executescript(
            """
            CREATE TABLE decoded_entity(entity_type TEXT, stable_id TEXT);
            CREATE TABLE topology_edge(
              topology_edge_id INTEGER PRIMARY KEY, from_room INTEGER,
              direction TEXT, to_room INTEGER, door INTEGER, hidden INTEGER,
              source_row_id INTEGER, direction_offset INTEGER,
              target_offset INTEGER, hidden_source_row_id INTEGER
            );
            CREATE TABLE import_run(singleton INTEGER, schema_version INTEGER, semantic_sha256 TEXT);
            INSERT INTO decoded_entity VALUES('room','room:1'),('room','room:2');
            INSERT INTO topology_edge VALUES(1,1,'E',2,0,0,10,170,30,NULL);
            INSERT INTO topology_edge VALUES(2,1,'N',2,1,0,11,171,34,NULL);
            INSERT INTO topology_edge VALUES(3,2,'W',1,0,0,12,170,30,NULL);
            INSERT INTO import_run VALUES(1,1,'fixture-semantic');
            """
        )
        connection.commit()
        connection.close()
        return path

    def graph(self) -> Path:
        path = self.root / "graph.json"
        path.write_text(json.dumps({
            "nodes": [
                {"id":"1","r":"R1","x":0,"y":0,"is_store":1,"spawn_total":1},
                {"id":"2","r":"R1","x":1,"y":0,"is_tavern":1},
            ],
            "edges": [
                {"id":"old","source":"1","target":"2","dir":"E","door":0,"hidden":0},
                {"id":"back","source":"2","target":"1","dir":"W","door":0,"hidden":0},
            ],
            "regionNames":{"R1":"Fixture"},
        }), encoding="utf-8")
        return path

    def test_loading_preserves_canonical_multiedges_and_closes_database(self):
        baseline = self.baseline()
        before = baseline.stat().st_mtime_ns
        rooms, edges, metadata = read_canonical_topology(baseline)
        self.assertEqual(rooms, ["1", "2"])
        self.assertEqual(len(edges), 3)
        self.assertEqual([edge["dir"] for edge in edges[:2]], ["E", "N"])
        self.assertEqual(metadata["semantic_sha256"], "fixture-semantic")
        self.assertEqual(baseline.stat().st_mtime_ns, before)
        baseline.unlink()

    def test_combining_nodes_reports_identity_differences(self):
        graph = json.loads(self.graph().read_text(encoding="utf-8"))
        combined, differences = combine_with_derived_nodes(["1", "3"], [], graph)
        self.assertEqual([node["id"] for node in combined["nodes"]], ["1", "3"])
        self.assertEqual(differences["canonical_rooms_missing_derived_attributes"], ["3"])
        self.assertEqual(differences["derived_rooms_missing_canonical_identity"], ["2"])

    def test_report_identifies_recovered_edge_and_metric_delta(self):
        report = build_report(self.baseline(), self.graph())
        comparison = report["comparison_with_derived_graph"]
        self.assertEqual(comparison["recovered_edge_count"], 1)
        self.assertEqual(comparison["recovered_edges"][0]["direction"], "N")
        self.assertEqual(comparison["recovered_edges"][0]["source_row_id"], 11)
        self.assertEqual(comparison["deltas_canonical_minus_derived"]["edge_records"], 1)
        self.assertEqual(report["counts"]["edge_records"], 3)

    def test_markdown_excludes_descriptions_and_is_deterministic(self):
        graph = json.loads(self.graph().read_text(encoding="utf-8"))
        graph["nodes"][0]["l"] = "PRIVATE DESCRIPTION"
        self.graph().write_text(json.dumps(graph), encoding="utf-8")
        report = build_report(self.baseline(), self.graph())
        first = render_markdown(report)
        second = render_markdown(report)
        self.assertEqual(first, second)
        self.assertNotIn("PRIVATE DESCRIPTION", first)
        self.assertIn("recovered edges", first)


if __name__ == "__main__":
    unittest.main()
