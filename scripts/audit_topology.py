#!/usr/bin/env python3
"""Audit the existing derived room graph without modifying its source file."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "source_paths.local.json"
DEFAULT_JSON = REPO_ROOT / "var" / "reports" / "topology-audit.json"
DEFAULT_MARKDOWN = REPO_ROOT / "docs" / "TOPOLOGY_AUDIT.md"
INVERSE_DIRECTION = {
    "N": "S", "S": "N", "E": "W", "W": "E",
    "NE": "SW", "SW": "NE", "NW": "SE", "SE": "NW",
    "U": "D", "D": "U",
}


def natural_key(value: Any) -> tuple[int, Any]:
    text = str(value)
    try:
        return (0, int(text))
    except ValueError:
        return (1, text)


def configured_source(config_path: Path, source_name: str) -> Path:
    with config_path.open("r", encoding="utf-8") as stream:
        config = json.load(stream)
    matches = [s for s in config.get("sources", []) if s.get("name") == source_name]
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one configured source named {source_name!r}; found {len(matches)}"
        )
    path = Path(os.path.expandvars(str(matches[0]["path"]))).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Configured {source_name!r} is not a file: {path}")
    return path.resolve(strict=True)


def load_graph(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    graph = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(graph, dict):
        raise ValueError("Graph root must be an object")
    if not isinstance(graph.get("nodes"), list) or not isinstance(graph.get("edges"), list):
        raise ValueError("Graph must contain node and edge arrays")
    if not isinstance(graph.get("regionNames", {}), dict):
        raise ValueError("regionNames must be an object when present")
    return graph, hashlib.sha256(raw).hexdigest()


def components(
    nodes: Iterable[str], adjacency: dict[str, set[str]]
) -> list[list[str]]:
    unseen = set(nodes)
    result: list[list[str]] = []
    while unseen:
        seed = min(unseen, key=natural_key)
        unseen.remove(seed)
        stack = [seed]
        component: list[str] = []
        while stack:
            node = stack.pop()
            component.append(node)
            neighbors = sorted(adjacency.get(node, ()), key=natural_key, reverse=True)
            for neighbor in neighbors:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
        result.append(sorted(component, key=natural_key))
    return sorted(result, key=lambda c: (-len(c), natural_key(c[0])))


def strongly_connected_components(
    nodes: Iterable[str], forward: dict[str, set[str]], reverse: dict[str, set[str]]
) -> list[list[str]]:
    ordered_nodes = sorted(set(nodes), key=natural_key)
    visited: set[str] = set()
    finish: list[str] = []
    for seed in ordered_nodes:
        if seed in visited:
            continue
        visited.add(seed)
        stack: list[tuple[str, bool]] = [(seed, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                finish.append(node)
                continue
            stack.append((node, True))
            for neighbor in sorted(forward.get(node, ()), key=natural_key, reverse=True):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, False))

    visited.clear()
    result: list[list[str]] = []
    for seed in reversed(finish):
        if seed in visited:
            continue
        visited.add(seed)
        stack = [seed]
        component: list[str] = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in sorted(reverse.get(node, ()), key=natural_key, reverse=True):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        result.append(sorted(component, key=natural_key))
    return sorted(result, key=lambda c: (-len(c), natural_key(c[0])))


def reachable(seed: str, adjacency: dict[str, set[str]]) -> set[str]:
    found = {seed}
    queue = deque([seed])
    while queue:
        for neighbor in adjacency.get(queue.popleft(), ()):
            if neighbor not in found:
                found.add(neighbor)
                queue.append(neighbor)
    return found


def component_summary(groups: list[list[str]], include_members: bool = False) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "count": len(groups),
        "sizes": [len(group) for group in groups],
    }
    if include_members:
        summary["members"] = groups
    return summary


def edge_ref(index: int, edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "index": index,
        "id": str(edge.get("id", "")),
        "source": str(edge.get("source", "")),
        "target": str(edge.get("target", "")),
        "direction": str(edge.get("dir", "")),
        "door": bool(edge.get("door", 0)),
        "hidden": bool(edge.get("hidden", 0)),
    }


def _duplicate_groups(values: list[str]) -> list[dict[str, Any]]:
    positions: dict[str, list[int]] = defaultdict(list)
    for index, value in enumerate(values):
        positions[value].append(index)
    return [
        {"value": value, "indices": positions[value]}
        for value in sorted(positions, key=natural_key)
        if len(positions[value]) > 1
    ]


def rank_regions(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]], region_names: dict[str, Any]
) -> list[dict[str, Any]]:
    node_regions = {str(n.get("id", "")): str(n.get("r", "<missing>")) for n in nodes}
    metrics: dict[str, dict[str, Any]] = {}
    for region in set(node_regions.values()) | set(map(str, region_names)):
        metrics[region] = {
            "region_id": region,
            "region_name": str(region_names.get(region, "<unnamed>")),
            "room_count": 0,
            "door_edges": 0,
            "hidden_edges": 0,
            "vertical_edges": 0,
            "diagonal_edges": 0,
            "portal_rooms": 0,
            "transport_rooms": 0,
            "store_rooms": 0,
            "tavern_rooms": 0,
            "quest_rooms": 0,
            "trainer_rooms": 0,
            "trap_rooms": 0,
            "spawn_rooms": 0,
            "cross_region_edges": 0,
        }
    for node in nodes:
        region = str(node.get("r", "<missing>"))
        item = metrics[region]
        item["room_count"] += 1
        item["portal_rooms"] += int(bool(node.get("portal", 0)))
        item["transport_rooms"] += int(bool(node.get("tp", 0)))
        item["store_rooms"] += int(bool(node.get("is_store", 0)))
        item["tavern_rooms"] += int(bool(node.get("is_tavern", 0)))
        item["quest_rooms"] += int(bool(node.get("is_quest", 0)))
        trainer = node.get("is_spell_trainer", 0) or node.get("skill_code") is not None or node.get("attr_code") is not None
        item["trainer_rooms"] += int(bool(trainer))
        item["trap_rooms"] += int(bool(node.get("has_trap", 0)))
        item["spawn_rooms"] += int(node.get("spawn_total") is not None)
    for edge in edges:
        source_region = node_regions.get(str(edge.get("source", "")))
        target_region = node_regions.get(str(edge.get("target", "")))
        if source_region not in metrics:
            continue
        item = metrics[source_region]
        item["door_edges"] += int(bool(edge.get("door", 0)))
        item["hidden_edges"] += int(bool(edge.get("hidden", 0)))
        item["vertical_edges"] += int(edge.get("dir") in {"U", "D"})
        item["diagonal_edges"] += int(edge.get("dir") in {"NE", "NW", "SE", "SW"})
        item["cross_region_edges"] += int(target_region is not None and source_region != target_region)

    feature_fields = [
        "door_edges", "hidden_edges", "vertical_edges", "diagonal_edges",
        "portal_rooms", "transport_rooms", "store_rooms", "tavern_rooms",
        "quest_rooms", "trainer_rooms", "trap_rooms", "spawn_rooms",
        "cross_region_edges",
    ]
    ranked = []
    for item in metrics.values():
        count = item["room_count"]
        practicality = 3 if 25 <= count <= 250 else 2 if 10 <= count <= 500 else 1
        present = [field for field in feature_fields if item[field] > 0]
        item["feature_categories_present"] = present
        item["score"] = practicality + len(present)
        item["score_explanation"] = {
            "practicality_points": practicality,
            "feature_points": len(present),
            "formula": "practicality_points + one point per present feature category",
        }
        ranked.append(item)
    return sorted(ranked, key=lambda x: (-x["score"], x["room_count"], natural_key(x["region_id"])))


def audit_graph(graph: dict[str, Any], source_path: Path, source_sha256: str) -> dict[str, Any]:
    nodes = graph["nodes"]
    edges = graph["edges"]
    if any(not isinstance(n, dict) for n in nodes) or any(not isinstance(e, dict) for e in edges):
        raise ValueError("Every node and edge must be an object")

    node_ids = [str(node.get("id", "")) for node in nodes]
    edge_ids = [str(edge.get("id", "")) for edge in edges]
    unique_nodes = set(node_ids)
    node_by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_by_id.setdefault(str(node.get("id", "")), node)

    duplicate_nodes = _duplicate_groups(node_ids)
    duplicate_edges = _duplicate_groups(edge_ids)
    endpoint_valid_edges: list[tuple[int, dict[str, Any]]] = []
    dangling = []
    unknown_directions = []
    logical: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    forward: dict[str, set[str]] = defaultdict(set)
    reverse: dict[str, set[str]] = defaultdict(set)
    undirected: dict[str, set[str]] = defaultdict(set)
    for index, edge in enumerate(edges):
        source, target = str(edge.get("source", "")), str(edge.get("target", ""))
        direction = str(edge.get("dir", ""))
        logical[(source, target, direction)].append(index)
        if direction not in INVERSE_DIRECTION:
            unknown_directions.append(edge_ref(index, edge))
        missing = [name for name, value in (("source", source), ("target", target)) if value not in unique_nodes]
        if missing:
            item = edge_ref(index, edge)
            item["missing_endpoints"] = missing
            dangling.append(item)
            continue
        endpoint_valid_edges.append((index, edge))
        forward[source].add(target)
        reverse[target].add(source)
        undirected[source].add(target)
        undirected[target].add(source)

    weak = components(unique_nodes, undirected)
    strong = strongly_connected_components(unique_nodes, forward, reverse)
    seed = min(weak[0], key=natural_key) if weak else None
    from_seed = reachable(seed, forward) if seed is not None else set()
    to_seed = reachable(seed, reverse) if seed is not None else set()

    reverse_lookup: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, edge in endpoint_valid_edges:
        reverse_lookup[(str(edge.get("source", "")), str(edge.get("target", "")), str(edge.get("dir", "")))].append((index, edge))
    missing_reverse = []
    inconsistent_pairs: dict[tuple[int, int], dict[str, Any]] = {}
    consistent_pair_keys: set[tuple[int, int]] = set()
    for index, edge in endpoint_valid_edges:
        direction = str(edge.get("dir", ""))
        inverse = INVERSE_DIRECTION.get(direction)
        candidates = reverse_lookup.get((str(edge.get("target", "")), str(edge.get("source", "")), inverse), []) if inverse else []
        if not candidates:
            missing_reverse.append(edge_ref(index, edge))
            continue
        matching = [
            (other_index, other) for other_index, other in candidates
            if bool(other.get("door", 0)) == bool(edge.get("door", 0))
            and bool(other.get("hidden", 0)) == bool(edge.get("hidden", 0))
        ]
        if matching:
            for other_index, _ in matching:
                consistent_pair_keys.add(tuple(sorted((index, other_index))))
        else:
            for other_index, other in candidates:
                key = tuple(sorted((index, other_index)))
                inconsistent_pairs[key] = {
                    "edge": edge_ref(index, edge),
                    "reverse_edge": edge_ref(other_index, other),
                    "door_matches": bool(edge.get("door", 0)) == bool(other.get("door", 0)),
                    "hidden_matches": bool(edge.get("hidden", 0)) == bool(other.get("hidden", 0)),
                }

    node_regions = {node_id: str(node_by_id[node_id].get("r", "<missing>")) for node_id in unique_nodes}
    cross_region = []
    region_pair_counts: Counter[tuple[str, str]] = Counter()
    vertical = []
    for index, edge in endpoint_valid_edges:
        ref = edge_ref(index, edge)
        if edge.get("dir") in {"U", "D"}:
            vertical.append(ref)
        source_region = node_regions[str(edge.get("source", ""))]
        target_region = node_regions[str(edge.get("target", ""))]
        if source_region != target_region:
            ref["source_region"] = source_region
            ref["target_region"] = target_region
            cross_region.append(ref)
            region_pair_counts[(source_region, target_region)] += 1

    special_nodes = {
        flag: sorted(
            [str(node.get("id", "")) for node in nodes if bool(node.get(flag, 0))],
            key=natural_key,
        )
        for flag in ("portal", "tp")
    }
    special_connectivity = {}
    for flag, ids in special_nodes.items():
        id_set = set(ids)
        special_connectivity[flag] = {
            "node_ids": ids,
            "incident_edge_count": sum(
                1 for _, edge in endpoint_valid_edges
                if str(edge.get("source", "")) in id_set or str(edge.get("target", "")) in id_set
            ),
            "isolated_node_ids": [node_id for node_id in ids if not undirected.get(node_id)],
        }

    special_node_ids = set(special_nodes["portal"]) | set(special_nodes["tp"])
    reverse_endpoint_directions: dict[tuple[str, str], set[str]] = defaultdict(set)
    for _, edge in endpoint_valid_edges:
        reverse_endpoint_directions[
            (str(edge.get("source", "")), str(edge.get("target", "")))
        ].add(str(edge.get("dir", "")))

    structural_counts: Counter[str] = Counter()
    for item in missing_reverse:
        reverse_directions = sorted(
            reverse_endpoint_directions.get((item["target"], item["source"]), set())
        )
        if reverse_directions:
            classification = "reverse_endpoint_wrong_direction"
            item["reverse_endpoint_directions"] = reverse_directions
        elif item["door"]:
            classification = "one_way_door"
        elif item["hidden"]:
            classification = "one_way_hidden"
        elif item["direction"] in {"U", "D"}:
            classification = "one_way_vertical"
        elif node_regions.get(item["source"]) != node_regions.get(item["target"]):
            classification = "one_way_cross_region"
        elif item["source"] in special_node_ids or item["target"] in special_node_ids:
            classification = "one_way_special_endpoint"
        else:
            classification = "one_way_plain"
        item["structural_classification"] = classification
        structural_counts[classification] += 1

    missing_reverse_classification = {
        "structural_category_counts": dict(sorted(structural_counts.items())),
        "structural_category_priority": [
            "reverse endpoint with a non-inverse direction",
            "door",
            "hidden",
            "vertical",
            "cross-region",
            "portal/transport endpoint",
            "plain",
        ],
        "by_direction": dict(sorted(Counter(item["direction"] for item in missing_reverse).items())),
        "by_door_hidden_state": dict(sorted(Counter(
            "door+hidden" if item["door"] and item["hidden"] else
            "door" if item["door"] else "hidden" if item["hidden"] else "plain"
            for item in missing_reverse
        ).items())),
        "by_source_region": dict(sorted(Counter(
            node_regions.get(item["source"], "<missing>") for item in missing_reverse
        ).items())),
        "cross_region_count": sum(
            node_regions.get(item["source"]) != node_regions.get(item["target"])
            for item in missing_reverse
        ),
        "vertical_count": sum(item["direction"] in {"U", "D"} for item in missing_reverse),
        "incident_to_portal_or_transport_count": sum(
            item["source"] in special_node_ids or item["target"] in special_node_ids
            for item in missing_reverse
        ),
        "interpretation_limit": "These are descriptive groups, not claims that a one-way link is intentional or erroneous.",
    }

    invalid_coordinates = []
    coordinate_groups: dict[tuple[str, float, float], list[str]] = defaultdict(list)
    coordinates: dict[str, tuple[float, float]] = {}
    for index, node in enumerate(nodes):
        node_id = str(node.get("id", ""))
        x, y = node.get("x"), node.get("y")
        if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x) or not isinstance(y, (int, float)) or isinstance(y, bool) or not math.isfinite(y):
            invalid_coordinates.append({"index": index, "node_id": node_id, "x": x, "y": y})
            continue
        coords = (float(x), float(y))
        coordinates[node_id] = coords
        coordinate_groups[(node_regions.get(node_id, "<missing>"), *coords)].append(node_id)
    collisions = [
        {"region_id": key[0], "x": key[1], "y": key[2], "node_ids": sorted(ids, key=natural_key)}
        for key, ids in sorted(coordinate_groups.items()) if len(ids) > 1
    ]
    delta_counts: dict[str, Counter[tuple[float, float]]] = defaultdict(Counter)
    zero_distance = []
    for index, edge in endpoint_valid_edges:
        source, target = str(edge.get("source", "")), str(edge.get("target", ""))
        if source in coordinates and target in coordinates:
            delta = (coordinates[target][0] - coordinates[source][0], coordinates[target][1] - coordinates[source][1])
            delta_counts[str(edge.get("dir", ""))][delta] += 1
            if delta == (0.0, 0.0):
                zero_distance.append(edge_ref(index, edge))
    delta_summary = {
        direction: [
            {"dx": delta[0], "dy": delta[1], "count": count}
            for delta, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:10]
        ]
        for direction, counter in sorted(delta_counts.items())
    }

    logical_duplicates = [
        {"source": key[0], "target": key[1], "direction": key[2], "indices": indices}
        for key, indices in sorted(logical.items()) if len(indices) > 1
    ]
    region_names = {str(k): str(v) for k, v in graph.get("regionNames", {}).items()}
    return {
        "audit_version": 1,
        "source": {
            "configured_name": "derived_graph",
            "path": str(source_path),
            "sha256": source_sha256,
            "source_classification": "noncanonical derived output; read only",
        },
        "counts": {
            "node_records": len(nodes),
            "unique_node_ids": len(unique_nodes),
            "edge_records": len(edges),
            "endpoint_valid_edges": len(endpoint_valid_edges),
            "region_ids_on_nodes": len(set(node_regions.values())),
        },
        "integrity": {
            "duplicate_node_ids": duplicate_nodes,
            "duplicate_edge_ids": duplicate_edges,
            "duplicate_logical_edges": logical_duplicates,
            "dangling_edges": dangling,
            "unknown_direction_edges": unknown_directions,
        },
        "connectivity": {
            "weak_components": component_summary(weak, include_members=True),
            "strong_components": component_summary(strong, include_members=True),
            "reachability": {
                "deterministic_seed": seed,
                "seed_rule": "natural-lowest room ID in the largest weak component",
                "reachable_from_seed_count": len(from_seed),
                "unreachable_from_seed": sorted(unique_nodes - from_seed, key=natural_key),
                "can_reach_seed_count": len(to_seed),
                "cannot_reach_seed": sorted(unique_nodes - to_seed, key=natural_key),
                "zero_out_degree_nodes": sorted([n for n in unique_nodes if not forward.get(n)], key=natural_key),
                "zero_in_degree_nodes": sorted([n for n in unique_nodes if not reverse.get(n)], key=natural_key),
            },
        },
        "reverse_counterparts": {
            "direction_map": INVERSE_DIRECTION,
            "missing_count": len(missing_reverse),
            "missing": missing_reverse,
            "missing_classification": missing_reverse_classification,
            "consistent_pair_count": len(consistent_pair_keys),
            "door_or_hidden_inconsistent_pair_count": len(inconsistent_pairs),
            "door_or_hidden_inconsistent_pairs": [inconsistent_pairs[k] for k in sorted(inconsistent_pairs)],
        },
        "special_topology": {
            "vertical_edge_count": len(vertical),
            "vertical_edges": vertical,
            "portal_nodes": special_connectivity["portal"],
            "transport_nodes": special_connectivity["tp"],
            "cross_region_edge_count": len(cross_region),
            "cross_region_edges": cross_region,
            "directed_region_pair_counts": [
                {"source_region": key[0], "target_region": key[1], "count": count}
                for key, count in sorted(region_pair_counts.items())
            ],
        },
        "derived_layout_audit": {
            "classification": "x, y, and region membership are derived presentation data, not source-authored world facts",
            "invalid_coordinate_nodes": invalid_coordinates,
            "same_region_coordinate_collision_count": len(collisions),
            "same_region_coordinate_collisions": collisions,
            "zero_distance_edge_count": len(zero_distance),
            "zero_distance_edges": zero_distance,
            "most_common_coordinate_deltas_by_direction": delta_summary,
            "interpretation_limit": "Delta frequencies are descriptive only; this audit does not treat coordinates as canonical geometry.",
        },
        "golden_fixture_region_ranking": {
            "criteria": {
                "practicality": "3 points for 25-250 rooms; 2 for 10-500; otherwise 1",
                "diversity": "1 point for each present category: doors, hidden exits, vertical links, diagonals, portals, transports, stores, taverns, quests, trainers, traps, spawns, cross-region links",
                "tie_breakers": "fewer rooms, then natural region ID",
                "selection_limit": "Ranking identifies candidates; a reviewed room subset must be chosen after canonical Phase 1 data exists.",
            },
            "regions": rank_regions(nodes, edges, region_names),
        },
        "limitations": [
            "The input graph is derived and noncanonical.",
            "Phase 1 raw provenance import and baseline reconciliation are incomplete.",
            "This audit describes topology but cannot confirm gameplay intent or source-authored semantics.",
            "Portal and transport analysis uses existing graph flags whose decoding remains to be revalidated.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    integrity = report["integrity"]
    connectivity = report["connectivity"]
    reverse = report["reverse_counterparts"]
    special = report["special_topology"]
    layout = report["derived_layout_audit"]
    regions = report["golden_fixture_region_ranking"]["regions"][:10]
    lines = [
        "# Phase 2 Topology Audit",
        "",
        "> Historical derived-graph baseline: canonical Phase 2 metrics now use all 7,097 source-decoded edges and are documented in `docs/CANONICAL_TOPOLOGY_AUDIT.md`.",
        "",
        "This report is generated from the configured `derived_graph` source. The source was read only. Room descriptions are intentionally excluded.",
        "",
        "## Summary",
        "",
        f"- {counts['node_records']:,} node records ({counts['unique_node_ids']:,} unique IDs)",
        f"- {counts['edge_records']:,} directed edge records ({counts['endpoint_valid_edges']:,} with valid endpoints)",
        f"- {len(integrity['duplicate_node_ids']):,} duplicate node-ID groups; {len(integrity['duplicate_edge_ids']):,} duplicate edge-ID groups",
        f"- {len(integrity['dangling_edges']):,} dangling edges; {len(integrity['unknown_direction_edges']):,} edges with unknown directions",
        f"- {connectivity['weak_components']['count']:,} weak components; {connectivity['strong_components']['count']:,} strong components",
        f"- {reverse['missing_count']:,} directed edges lack an inverse-direction counterpart",
        "- Structural asymmetry categories: " + ", ".join(
            f"{name}={count:,}" for name, count in
            reverse["missing_classification"]["structural_category_counts"].items()
        ),
        f"- {reverse['door_or_hidden_inconsistent_pair_count']:,} reverse pairs disagree on door or hidden state",
        f"- {special['vertical_edge_count']:,} vertical edges; {special['cross_region_edge_count']:,} cross-region edges",
        f"- {len(special['portal_nodes']['node_ids']):,} portal-flagged rooms; {len(special['transport_nodes']['node_ids']):,} transport-flagged rooms",
        f"- {layout['same_region_coordinate_collision_count']:,} same-region coordinate collisions; {layout['zero_distance_edge_count']:,} zero-distance edges",
        "",
        "## Reachability",
        "",
        f"The deterministic seed is room `{connectivity['reachability']['deterministic_seed']}` (the natural-lowest ID in the largest weak component). "
        f"It reaches {connectivity['reachability']['reachable_from_seed_count']:,} rooms; "
        f"{len(connectivity['reachability']['unreachable_from_seed']):,} rooms are not reachable from it by directed links.",
        "",
        "## Golden-fixture candidates",
        "",
        "Scores award practicality points by room count plus one point for each topology/gameplay feature category present. This is a candidate ranking, not a final selection.",
        "",
        "| Rank | Region | Name | Rooms | Score | Present categories |",
        "|---:|---|---|---:|---:|---|",
    ]
    for rank, item in enumerate(regions, 1):
        name = item["region_name"].replace("|", "\\|")
        features = ", ".join(item["feature_categories_present"])
        lines.append(f"| {rank} | `{item['region_id']}` | {name} | {item['room_count']} | {item['score']} | {features} |")
    lines += [
        "",
        "## Interpretation limits",
        "",
        "Coordinates and region membership are derived presentation data, not original world facts. Phase 1 provenance import and baseline reconciliation are still incomplete, so this audit cannot determine whether asymmetric links or flag disagreements are intentional. The detailed machine-readable report is generated under ignored `var/reports/topology-audit.json`.",
        "",
    ]
    return "\n".join(lines)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--check", action="store_true", help="audit without writing outputs")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        graph_path = configured_source(args.config.resolve(strict=True), "derived_graph")
        graph, source_sha256 = load_graph(graph_path)
        report = audit_graph(graph, graph_path, source_sha256)
        if not args.check:
            write_text(args.json_output.resolve(), json.dumps(report, indent=2, ensure_ascii=False) + "\n")
            write_text(args.markdown_output.resolve(), render_markdown(report))
        print(
            f"Audited {report['counts']['node_records']} nodes and "
            f"{report['counts']['edge_records']} edges; "
            f"{report['reverse_counterparts']['missing_count']} lack reverse counterparts."
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"topology audit error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
