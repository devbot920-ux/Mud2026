#!/usr/bin/env python3
"""Audit Phase 1 canonical topology and compare it with the derived graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

try:
    from scripts.audit_topology import audit_graph, load_graph, natural_key
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from audit_topology import audit_graph, load_graph, natural_key


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "source_paths.local.json"
DEFAULT_BASELINE = ROOT / "var" / "baseline" / "rose-baseline.sqlite"
DEFAULT_JSON = ROOT / "var" / "reports" / "canonical-topology-audit.json"
DEFAULT_MARKDOWN = ROOT / "docs" / "CANONICAL_TOPOLOGY_AUDIT.md"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def configured_graph(config_path: Path) -> Path:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    matches = [source for source in config.get("sources", []) if source.get("name") == "derived_graph"]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one derived_graph source; found {len(matches)}")
    path = Path(os.path.expandvars(str(matches[0]["path"]))).expanduser()
    return path.resolve(strict=True)


def read_canonical_topology(path: Path) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Canonical baseline does not exist; run scripts/baseline_import.py first: {path}")
    uri = path.resolve().as_uri() + "?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"Canonical baseline integrity check failed: {integrity}")
        room_ids = [
            stable_id.split(":", 1)[1]
            for (stable_id,) in connection.execute(
                "SELECT DISTINCT stable_id FROM decoded_entity "
                "WHERE entity_type='room' ORDER BY stable_id"
            )
        ]
        rows = connection.execute(
            "SELECT topology_edge_id,from_room,direction,to_room,door,hidden,"
            "source_row_id,direction_offset,target_offset,hidden_source_row_id "
            "FROM topology_edge ORDER BY topology_edge_id"
        ).fetchall()
        edges = [
            {
                "id": f"canonical:{row[0]}",
                "source": str(row[1]),
                "target": str(row[3]),
                "dir": str(row[2]),
                "door": int(row[4]),
                "hidden": int(row[5]),
                "topology_edge_id": row[0],
                "source_row_id": row[6],
                "direction_offset": row[7],
                "target_offset": row[8],
                "hidden_source_row_id": row[9],
            }
            for row in rows
        ]
        run = connection.execute(
            "SELECT schema_version,semantic_sha256 FROM import_run WHERE singleton=1"
        ).fetchone()
        metadata = {
            "path": str(path.resolve()),
            "sha256": sha256_file(path),
            "schema_version": run[0],
            "semantic_sha256": run[1],
            "integrity_check": integrity,
        }
        return sorted(room_ids, key=natural_key), edges, metadata
    finally:
        connection.close()


def combine_with_derived_nodes(
    room_ids: list[str], edges: list[dict[str, Any]], derived: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    derived_by_id = {str(node.get("id", "")): node for node in derived["nodes"]}
    canonical_ids = set(room_ids)
    derived_ids = set(derived_by_id)
    nodes = []
    for room_id in room_ids:
        if room_id in derived_by_id:
            nodes.append(dict(derived_by_id[room_id]))
        else:
            nodes.append({"id": room_id, "r": "<missing>", "x": None, "y": None})
    differences = {
        "canonical_rooms_missing_derived_attributes": sorted(canonical_ids - derived_ids, key=natural_key),
        "derived_rooms_missing_canonical_identity": sorted(derived_ids - canonical_ids, key=natural_key),
    }
    return {
        "nodes": nodes,
        "edges": edges,
        "regionNames": derived.get("regionNames", {}),
    }, differences


def semantic_edge(edge: dict[str, Any]) -> tuple[str, str, str, int, int]:
    return (
        str(edge.get("source", "")),
        str(edge.get("target", "")),
        str(edge.get("dir", "")),
        int(bool(edge.get("door", 0))),
        int(bool(edge.get("hidden", 0))),
    )


def metric_snapshot(report: dict[str, Any]) -> dict[str, int]:
    reachability = report["connectivity"]["reachability"]
    reverse = report["reverse_counterparts"]
    special = report["special_topology"]
    integrity = report["integrity"]
    layout = report["derived_layout_audit"]
    return {
        "edge_records": report["counts"]["edge_records"],
        "duplicate_node_id_groups": len(integrity["duplicate_node_ids"]),
        "duplicate_edge_id_groups": len(integrity["duplicate_edge_ids"]),
        "duplicate_logical_edge_groups": len(integrity["duplicate_logical_edges"]),
        "dangling_edges": len(integrity["dangling_edges"]),
        "unknown_direction_edges": len(integrity["unknown_direction_edges"]),
        "weak_components": report["connectivity"]["weak_components"]["count"],
        "strong_components": report["connectivity"]["strong_components"]["count"],
        "reachable_from_seed": reachability["reachable_from_seed_count"],
        "unreachable_from_seed": len(reachability["unreachable_from_seed"]),
        "can_reach_seed": reachability["can_reach_seed_count"],
        "cannot_reach_seed": len(reachability["cannot_reach_seed"]),
        "zero_out_degree_rooms": len(reachability["zero_out_degree_nodes"]),
        "zero_in_degree_rooms": len(reachability["zero_in_degree_nodes"]),
        "missing_reverse_counterparts": reverse["missing_count"],
        "door_or_hidden_inconsistent_pairs": reverse["door_or_hidden_inconsistent_pair_count"],
        "vertical_edges": special["vertical_edge_count"],
        "cross_region_edges": special["cross_region_edge_count"],
        "portal_rooms": len(special["portal_nodes"]["node_ids"]),
        "transport_rooms": len(special["transport_nodes"]["node_ids"]),
        "same_region_coordinate_collisions": layout["same_region_coordinate_collision_count"],
        "zero_distance_edges": layout["zero_distance_edge_count"],
    }


def compare_reports(
    canonical: dict[str, Any], derived: dict[str, Any], recovered_edges: list[dict[str, Any]]
) -> dict[str, Any]:
    canonical_metrics = metric_snapshot(canonical)
    derived_metrics = metric_snapshot(derived)
    return {
        "canonical_metrics": canonical_metrics,
        "derived_metrics": derived_metrics,
        "deltas_canonical_minus_derived": {
            key: canonical_metrics[key] - derived_metrics[key] for key in canonical_metrics
        },
        "recovered_edge_count": len(recovered_edges),
        "recovered_edges": recovered_edges,
        "structural_category_counts": {
            "canonical": canonical["reverse_counterparts"]["missing_classification"]["structural_category_counts"],
            "derived": derived["reverse_counterparts"]["missing_classification"]["structural_category_counts"],
        },
    }


def build_report(baseline_path: Path, graph_path: Path) -> dict[str, Any]:
    derived, graph_sha256 = load_graph(graph_path)
    room_ids, canonical_edges, baseline_metadata = read_canonical_topology(baseline_path)
    combined, identity_differences = combine_with_derived_nodes(room_ids, canonical_edges, derived)
    canonical_report = audit_graph(combined, baseline_path, baseline_metadata["sha256"])
    derived_report = audit_graph(derived, graph_path, graph_sha256)

    derived_edges = {semantic_edge(edge) for edge in derived["edges"]}
    recovered = [
        {
            "topology_edge_id": edge["topology_edge_id"],
            "source": edge["source"],
            "target": edge["target"],
            "direction": edge["dir"],
            "door": bool(edge["door"]),
            "hidden": bool(edge["hidden"]),
            "source_row_id": edge["source_row_id"],
            "direction_offset": edge["direction_offset"],
            "target_offset": edge["target_offset"],
            "hidden_source_row_id": edge["hidden_source_row_id"],
        }
        for edge in canonical_edges
        if semantic_edge(edge) not in derived_edges
    ]
    recovered.sort(key=lambda item: item["topology_edge_id"])

    canonical_report["source"] = {
        "configured_name": "phase1_canonical_topology",
        "baseline": baseline_metadata,
        "supporting_derived_graph": {
            "path": str(graph_path),
            "sha256": graph_sha256,
            "usage": "room display attributes, derived regions, coordinates, and feature flags only",
        },
        "source_classification": "source-decoded topology with derived presentation attributes",
    }
    canonical_report["room_identity_reconciliation"] = identity_differences
    canonical_report["comparison_with_derived_graph"] = compare_reports(
        canonical_report, derived_report, recovered
    )
    canonical_report["limitations"] = [
        "Topology edges and room identities come from the Phase 1 baseline using tentative decoding rules.",
        "Regions, coordinates, portal/transport flags, and other presentation attributes still come from the derived graph.",
        "Structural asymmetry does not establish whether a connection is intentional gameplay or a decoding error.",
    ]
    return canonical_report


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    connectivity = report["connectivity"]
    reverse = report["reverse_counterparts"]
    special = report["special_topology"]
    comparison = report["comparison_with_derived_graph"]
    ranking = report["golden_fixture_region_ranking"]["regions"][:5]
    deltas = comparison["deltas_canonical_minus_derived"]
    lines = [
        "# Canonical Phase 2 Topology Audit",
        "",
        "This report uses room identities and all topology edges from the Phase 1 canonical baseline. Derived `graph.json` data is used only for regions, coordinates, and presentation/gameplay flags. Room descriptions are excluded.",
        "",
        "## Canonical summary",
        "",
        f"- {counts['node_records']:,} rooms and {counts['edge_records']:,} source-decoded directed edges",
        f"- {connectivity['weak_components']['count']:,} weak components and {connectivity['strong_components']['count']:,} strong components",
        f"- Seed room `{connectivity['reachability']['deterministic_seed']}` reaches {connectivity['reachability']['reachable_from_seed_count']:,} rooms; {len(connectivity['reachability']['unreachable_from_seed']):,} remain unreachable from it",
        f"- {reverse['missing_count']:,} edges lack an inverse-direction counterpart",
        "- Structural asymmetry categories: " + ", ".join(
            f"{name}={count:,}" for name, count in
            reverse["missing_classification"]["structural_category_counts"].items()
        ),
        f"- {reverse['door_or_hidden_inconsistent_pair_count']:,} reverse pairs disagree on door or hidden state",
        f"- {special['vertical_edge_count']:,} vertical edges and {special['cross_region_edge_count']:,} cross-region edges",
        "",
        "## Effect of the 20 recovered edges",
        "",
        f"The canonical baseline contains {comparison['recovered_edge_count']} semantic edges absent from the legacy graph. Exact edge tuples and source-row/byte-offset provenance are retained in the ignored machine-readable report.",
        "",
        "| Metric | Derived graph | Canonical | Change |",
        "|---|---:|---:|---:|",
    ]
    for key, canonical_value in comparison["canonical_metrics"].items():
        derived_value = comparison["derived_metrics"][key]
        lines.append(f"| {key.replace('_', ' ')} | {derived_value:,} | {canonical_value:,} | {deltas[key]:+,} |")
    lines += [
        "",
        "Recovered door multiedges account for most changes. In particular, the recovered links between rooms 3045 and 3046 connect the formerly separate 322-room component to the main world; the other recovered door directions substantially improve directed reachability and strong connectivity.",
        "",
        "## Golden-fixture candidates",
        "",
        "| Rank | Region | Name | Rooms | Score |",
        "|---:|---|---|---:|---:|",
    ]
    for index, item in enumerate(ranking, 1):
        lines.append(
            f"| {index} | `{item['region_id']}` | {item['region_name'].replace('|', chr(92) + '|')} | {item['room_count']} | {item['score']} |"
        )
    lines += [
        "",
        "Pendelhaven (`R02`) remains the leading fixture candidate because it ties for the highest feature score while remaining substantially smaller than Imperial City.",
        "",
        "## Interpretation limits",
        "",
        "The edge set is source-decoded but still based on tentative binary-offset interpretations. Regions, coordinates, and feature flags remain derived. Asymmetric links therefore remain structural findings rather than claims of gameplay intent.",
    ]
    return "\n".join(lines) + "\n"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        temporary.write_text(text, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        graph_path = configured_graph(args.config.resolve(strict=True))
        report = build_report(args.baseline.resolve(), graph_path)
        if not args.check:
            write_text(args.json_output.resolve(), json.dumps(report, indent=2, sort_keys=True) + "\n")
            write_text(args.markdown_output.resolve(), render_markdown(report))
        print(
            f"Audited {report['counts']['node_records']} rooms and "
            f"{report['counts']['edge_records']} canonical edges; "
            f"{report['reverse_counterparts']['missing_count']} lack reverse counterparts."
        )
        return 0
    except (OSError, ValueError, sqlite3.DatabaseError, KeyError, json.JSONDecodeError) as exc:
        print(f"canonical topology audit error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
