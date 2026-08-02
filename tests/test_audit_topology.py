import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_topology import (
    audit_graph,
    configured_source,
    load_graph,
    render_markdown,
)


def node(node_id, region="R1", x=0, y=0, **flags):
    value = {"id": str(node_id), "r": region, "x": x, "y": y, "portal": 0, "tp": 0}
    value.update(flags)
    return value


def edge(edge_id, source, target, direction, door=0, hidden=0):
    return {
        "id": edge_id,
        "source": str(source),
        "target": str(target),
        "dir": direction,
        "door": door,
        "hidden": hidden,
    }


class TopologyAuditTests(unittest.TestCase):
    def fixture(self):
        return {
            "nodes": [
                node(0, x=0, y=0, is_store=1, spawn_total=1),
                node(1, x=1, y=0, portal=1),
                node(2, x=1, y=1, tp=1),
                node(3, region="R2", x=0, y=0, is_tavern=1),
                node(4, region="R2", x=0, y=0),
                node(5, region="R3", x=9, y=9),
            ],
            "edges": [
                edge("a", 0, 1, "E", door=1),
                edge("b", 1, 0, "W", door=1),
                edge("c", 1, 2, "N", hidden=1),
                edge("d", 2, 1, "S", hidden=0),
                edge("e", 2, 3, "U"),
                edge("f", 3, 2, "D"),
                edge("g", 3, 4, "E"),
                edge("g", 3, 99, "SIDEWAYS"),
            ],
            "regionNames": {"R1": "One", "R2": "Two", "R3": "Three"},
        }

    def test_integrity_reverse_pairs_and_special_links(self):
        report = audit_graph(self.fixture(), Path("fixture.json"), "abc")
        self.assertEqual(report["counts"]["node_records"], 6)
        self.assertEqual(len(report["integrity"]["duplicate_edge_ids"]), 1)
        self.assertEqual(len(report["integrity"]["dangling_edges"]), 1)
        self.assertEqual(len(report["integrity"]["unknown_direction_edges"]), 1)
        self.assertEqual(report["reverse_counterparts"]["missing_count"], 1)
        self.assertEqual(report["reverse_counterparts"]["missing_classification"]["by_direction"], {"E": 1})
        self.assertEqual(
            report["reverse_counterparts"]["missing_classification"]["structural_category_counts"],
            {"one_way_plain": 1},
        )
        self.assertEqual(report["reverse_counterparts"]["door_or_hidden_inconsistent_pair_count"], 1)
        self.assertEqual(report["special_topology"]["vertical_edge_count"], 2)
        self.assertEqual(report["special_topology"]["cross_region_edge_count"], 2)

    def test_components_reachability_and_coordinate_audit(self):
        report = audit_graph(self.fixture(), Path("fixture.json"), "abc")
        connectivity = report["connectivity"]
        self.assertEqual(connectivity["weak_components"]["sizes"], [5, 1])
        self.assertEqual(connectivity["strong_components"]["sizes"], [4, 1, 1])
        self.assertEqual(connectivity["reachability"]["deterministic_seed"], "0")
        self.assertEqual(connectivity["reachability"]["unreachable_from_seed"], ["5"])
        layout = report["derived_layout_audit"]
        self.assertEqual(layout["same_region_coordinate_collision_count"], 1)
        self.assertEqual(layout["zero_distance_edge_count"], 1)

    def test_duplicate_nodes_and_logical_edges_are_reported(self):
        graph = self.fixture()
        graph["nodes"].append(node(1, x=7, y=7))
        graph["edges"].append(edge("z", 0, 1, "E", door=1))
        report = audit_graph(graph, Path("fixture.json"), "abc")
        self.assertEqual(report["integrity"]["duplicate_node_ids"][0]["indices"], [1, 6])
        self.assertEqual(report["integrity"]["duplicate_logical_edges"][0]["indices"], [0, 8])

    def test_wrong_reverse_direction_is_classified(self):
        graph = {
            "nodes": [node(1), node(2, x=1)],
            "edges": [edge("a", 1, 2, "E"), edge("b", 2, 1, "N")],
            "regionNames": {"R1": "One"},
        }
        report = audit_graph(graph, Path("fixture.json"), "abc")
        classification = report["reverse_counterparts"]["missing_classification"]
        self.assertEqual(
            classification["structural_category_counts"],
            {"reverse_endpoint_wrong_direction": 2},
        )
        self.assertEqual(
            report["reverse_counterparts"]["missing"][0]["reverse_endpoint_directions"],
            ["N"],
        )

    def test_region_ranking_is_auditable_and_deterministic(self):
        first = audit_graph(self.fixture(), Path("fixture.json"), "abc")
        second = audit_graph(self.fixture(), Path("fixture.json"), "abc")
        self.assertEqual(first, second)
        ranking = first["golden_fixture_region_ranking"]
        self.assertIn("practicality", ranking["criteria"])
        self.assertEqual(ranking["regions"][0]["region_id"], "R1")
        self.assertEqual(
            ranking["regions"][0]["score"],
            ranking["regions"][0]["score_explanation"]["practicality_points"]
            + ranking["regions"][0]["score_explanation"]["feature_points"],
        )

    def test_markdown_omits_room_descriptions(self):
        graph = self.fixture()
        graph["nodes"][0]["l"] = "SECRET LONG DESCRIPTION"
        report = audit_graph(graph, Path("fixture.json"), "abc")
        markdown = render_markdown(report)
        self.assertNotIn("SECRET LONG DESCRIPTION", markdown)
        self.assertIn("Phase 1 provenance import", markdown)

    def test_config_requires_exact_derived_graph_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            graph_path = root / "graph.json"
            graph_path.write_text("{}", encoding="utf-8")
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps({"sources": [{"name": "derived_graph", "path": str(graph_path)}]}),
                encoding="utf-8",
            )
            self.assertEqual(configured_source(config_path, "derived_graph"), graph_path.resolve())
            config_path.write_text(json.dumps({"sources": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                configured_source(config_path, "derived_graph")

    def test_loading_is_read_only_and_hashes_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph.json"
            raw = json.dumps(self.fixture()).encode("utf-8")
            path.write_bytes(raw)
            before = path.stat().st_mtime_ns
            graph, digest = load_graph(path)
            self.assertEqual(len(graph["nodes"]), 6)
            self.assertEqual(digest, hashlib.sha256(raw).hexdigest())
            self.assertEqual(path.stat().st_mtime_ns, before)

    def test_invalid_graph_shape_and_coordinates(self):
        with self.assertRaises(ValueError):
            audit_graph({"nodes": [], "edges": [1]}, Path("x"), "abc")
        graph = {"nodes": [node(0, x="bad", y=None)], "edges": [], "regionNames": {}}
        report = audit_graph(graph, Path("x"), "abc")
        self.assertEqual(len(report["derived_layout_audit"]["invalid_coordinate_nodes"]), 1)


if __name__ == "__main__":
    unittest.main()
