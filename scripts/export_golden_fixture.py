#!/usr/bin/env python3
"""Export the private Pendelhaven fixture using an engine-neutral JSON contract."""
from __future__ import annotations

import argparse, base64, hashlib, json, os, sqlite3, tempfile
from pathlib import Path
from typing import Any

try:
    from scripts.analyze_mod1_tags import KNOWN
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from analyze_mod1_tags import KNOWN

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "var" / "baseline" / "rose-baseline.sqlite"
DEFAULT_GRAPH = Path(r"C:\temp\DoorTelnet\graph.json")
DEFAULT_OUTPUT = ROOT / "var" / "exports" / "pendelhaven-v1.json"
CONTRACT_NAME = "mud2026.engine-neutral-world"
CONTRACT_VERSION = "1.0.0"
BASE_ENTITY_TAGS = {0x0A, 0x0D, 0x28, 0x30, 0x32}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ro_connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def source_provenance(connection: sqlite3.Connection, source_row_id: int) -> dict[str, Any]:
    row = connection.execute("""
      SELECT f.logical_name,r.table_name,r.source_row_id,r.source_identity_json,r.record_sha256
      FROM source_row r JOIN source_file f USING(source_file_id) WHERE r.source_row_id=?
    """, (source_row_id,)).fetchone()
    if row is None:
        raise ValueError(f"Missing source row {source_row_id}")
    return {"source": row["logical_name"], "table": row["table_name"],
            "source_row_id": row["source_row_id"], "record_sha256": row["record_sha256"],
            "identity": json.loads(row["source_identity_json"])}


def fields_for(connection: sqlite3.Connection, decoded_entity_id: int) -> list[dict[str, Any]]:
    result = []
    rows = connection.execute("""
      SELECT field_name,value_json,byte_offset,byte_width,decoding_rule,confidence,source_row_id
      FROM decoded_field WHERE decoded_entity_id=?
      ORDER BY field_name,coalesce(byte_offset,-1),decoded_field_id
    """, (decoded_entity_id,))
    for row in rows:
        provenance = source_provenance(connection, row["source_row_id"])
        provenance.update(byte_offset=row["byte_offset"], byte_width=row["byte_width"], rule=row["decoding_rule"])
        result.append({"name": row["field_name"], "value": json.loads(row["value_json"]),
                       "confidence": row["confidence"], "provenance": provenance})
    return result


def entity_rows(connection: sqlite3.Connection, entity_type: str, ids: set[int], scope: str) -> list[dict[str, Any]]:
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    rows = connection.execute(f"""
      SELECT decoded_entity_id,stable_id,source_row_id FROM decoded_entity
      WHERE entity_type=? AND CAST(substr(stable_id,instr(stable_id,':')+1) AS INTEGER) IN ({placeholders})
      ORDER BY CAST(substr(stable_id,instr(stable_id,':')+1) AS INTEGER),source_row_id
    """, (entity_type, *sorted(ids)))
    result = []
    for row in rows:
        entity_id = int(row["stable_id"].split(":", 1)[1])
        result.append({"id": entity_id, "stable_id": row["stable_id"], "scope": scope,
                       "fields": fields_for(connection, row["decoded_entity_id"]),
                       "provenance": source_provenance(connection, row["source_row_id"])})
    return result


def get_mod1_rows(connection: sqlite3.Connection, owner_keys: set[int]) -> list[dict[str, Any]]:
    if not owner_keys:
        return []
    placeholders = ",".join("?" for _ in owner_keys)
    rows = connection.execute(f"""
      SELECT r.source_row_id,r.record_sha256,r.source_identity_json,
             max(CASE WHEN v.column_name='key_0' THEN v.integer_value END) owner_key,
             max(CASE WHEN v.column_name='data' THEN v.blob_value END) data
      FROM source_row r JOIN source_file f USING(source_file_id) JOIN source_value v USING(source_row_id)
      WHERE f.logical_name='RCI_MOD1' AND r.table_name='data_t'
      GROUP BY r.source_row_id HAVING owner_key IN ({placeholders}) ORDER BY r.source_row_id
    """, tuple(sorted(owner_keys)))
    result = []
    for row in rows:
        data = row["data"]
        if not isinstance(data, bytes) or len(data) <= 8:
            tag, known = None, None
        else:
            tag, known = data[8], KNOWN.get(data[8])
        if tag in BASE_ENTITY_TAGS:
            continue
        provenance = source_provenance(connection, row["source_row_id"])
        provenance.update(byte_offset=8, byte_width=1, rule="MOD1 tag byte; complete raw record retained")
        result.append({"source_row_id": row["source_row_id"], "owner_key": row["owner_key"],
                       "tag": f"0x{tag:02X}" if tag is not None else "unknown",
                       "name": known[0] if known else None, "confidence": known[1] if known else "unknown",
                       "raw_data_base64": base64.b64encode(data or b"").decode("ascii"), "provenance": provenance})
    return result


def field_value(entity: dict[str, Any], name: str, default: Any = None) -> Any:
    return next((field["value"] for field in entity["fields"] if field["name"] == name), default)


def build_export(baseline: Path, graph_path: Path, region: str = "R02") -> dict[str, Any]:
    graph = json.loads(graph_path.read_text(encoding="utf-8-sig"))
    node_by_id = {int(node["id"]): node for node in graph["nodes"]}
    primary_ids = {node_id for node_id, node in node_by_id.items() if str(node.get("r")) == region}
    if not primary_ids:
        raise ValueError(f"Derived graph has no rooms in region {region}")
    connection = ro_connect(baseline)
    try:
        placeholders = ",".join("?" for _ in primary_ids)
        edges_raw = connection.execute(f"""
          SELECT * FROM topology_edge WHERE from_room IN ({placeholders}) OR to_room IN ({placeholders})
          ORDER BY topology_edge_id
        """, (*sorted(primary_ids), *sorted(primary_ids))).fetchall()
        stub_ids = {int(row["from_room"]) for row in edges_raw} | {int(row["to_room"]) for row in edges_raw}
        stub_ids -= primary_ids
        all_room_ids = primary_ids | stub_ids
        primary_rooms = entity_rows(connection, "room", primary_ids, "primary")
        stub_rooms = entity_rows(connection, "room", stub_ids, "stub")
        for stub in stub_rooms:
            # Boundary stubs prove edge endpoints without recursively importing
            # the neighboring region's content.
            stub["fields"] = [field for field in stub["fields"] if field["name"] == "room_id"]
        rooms = primary_rooms + stub_rooms
        if {room["id"] for room in rooms} != all_room_ids:
            raise ValueError("A primary or stub room is missing from the canonical baseline")
        for room in rooms:
            node = node_by_id.get(room["id"], {})
            room["display"] = {"classification": "derived presentation data", "region": node.get("r"),
                               "region_name": graph.get("regionNames", {}).get(str(node.get("r"))),
                               "x": node.get("x"), "y": node.get("y")}
        rooms.sort(key=lambda item: item["id"])
        edges = []
        for row in edges_raw:
            provenance = source_provenance(connection, row["source_row_id"])
            provenance.update(byte_offset=row["direction_offset"], byte_width=1,
                              rule=f"direction byte; target little-endian u32 at offset {row['target_offset']}")
            edge = {"id": row["topology_edge_id"], "from_room": row["from_room"], "to_room": row["to_room"],
                    "direction": row["direction"], "door": bool(row["door"]), "hidden": bool(row["hidden"]),
                    "provenance": provenance}
            if row["hidden_source_row_id"] is not None:
                edge["hidden_provenance"] = source_provenance(connection, row["hidden_source_row_id"])
            edges.append(edge)
        door_source_rows = {edge["provenance"]["source_row_id"] for edge in edges if edge["door"]}
        doors = []
        if door_source_rows:
            marks = ",".join("?" for _ in door_source_rows)
            for row in connection.execute(f"SELECT decoded_entity_id,stable_id,source_row_id FROM decoded_entity WHERE entity_type='door' AND source_row_id IN ({marks}) ORDER BY source_row_id", tuple(sorted(door_source_rows))):
                did = int(row["stable_id"].split(":", 1)[1])
                doors.append({"id": did, "stable_id": row["stable_id"], "scope": "primary" if did in primary_ids else "stub",
                              "fields": fields_for(connection, row["decoded_entity_id"]), "provenance": source_provenance(connection, row["source_row_id"])})
        spawns = entity_rows(connection, "spawn", primary_ids, "primary")
        npc_ids, item_ids = set(), set()
        for spawn in spawns:
            count = int(field_value(spawn, "spawn_count", 0) or 0)
            entries = []
            for index in range(1, min(count, 8) + 1):
                entry_type = field_value(spawn, f"spawn_{index}_type", "unknown")
                entry_id = field_value(spawn, f"spawn_{index}_id")
                entry = {"slot": index, "entity_type": entry_type, "entity_id": entry_id,
                         "count": field_value(spawn, f"spawn_{index}_count")}
                entries.append(entry)
                if entry_type == "npc" and entry_id is not None: npc_ids.add(int(entry_id))
                if entry_type == "item" and entry_id is not None: item_ids.add(int(entry_id))
            spawn["entries"] = entries
        npcs = entity_rows(connection, "npc", npc_ids, "referenced")
        items = entity_rows(connection, "item", item_ids, "referenced")
        modifier_keys = primary_ids | npc_ids | item_ids
        modifiers = get_mod1_rows(connection, modifier_keys)
        run = connection.execute("SELECT schema_version,semantic_sha256 FROM import_run WHERE singleton=1").fetchone()
    finally:
        connection.close()
    document = {
        "contract": {"name": CONTRACT_NAME, "version": CONTRACT_VERSION},
        "fixture": {"id": "pendelhaven-r02", "name": "Pendelhaven golden fixture", "primary_region": region,
                    "primary_room_ids": sorted(primary_ids), "stub_room_ids": sorted(stub_ids),
                    "boundary_rule": "all canonical edges touching a primary room; opposite endpoints become non-expanding stubs"},
        "sources": {"baseline": {"schema_version": run["schema_version"], "semantic_sha256": run["semantic_sha256"], "sha256": sha256_file(baseline)},
                    "derived_graph": {"sha256": sha256_file(graph_path), "usage": "region, coordinate, and display metadata only"}},
        "rooms": rooms, "edges": edges, "doors": doors, "npcs": npcs, "items": items,
        "spawns": spawns, "modifiers": modifiers,
    }
    validate_export(document)
    return document


def validate_export(document: dict[str, Any]) -> None:
    if document.get("contract") != {"name": CONTRACT_NAME, "version": CONTRACT_VERSION}:
        raise ValueError("Unsupported export contract")
    room_ids = [room["id"] for room in document["rooms"]]
    if len(room_ids) != len(set(room_ids)):
        raise ValueError("Duplicate room IDs")
    known_rooms = set(room_ids)
    for edge in document["edges"]:
        if edge["from_room"] not in known_rooms or edge["to_room"] not in known_rooms:
            raise ValueError(f"Dangling edge {edge['id']}")
    npc_ids = {entity["id"] for entity in document["npcs"]}
    item_ids = {entity["id"] for entity in document["items"]}
    for spawn in document["spawns"]:
        if spawn["id"] not in set(document["fixture"]["primary_room_ids"]):
            raise ValueError(f"Spawn {spawn['id']} is outside primary fixture")
        for entry in spawn.get("entries", []):
            if entry["entity_type"] == "npc" and entry["entity_id"] not in npc_ids:
                raise ValueError(f"Dangling NPC spawn reference {entry['entity_id']}")
            if entry["entity_type"] == "item" and entry["entity_id"] not in item_ids:
                raise ValueError(f"Dangling item spawn reference {entry['entity_id']}")
    if len({edge["id"] for edge in document["edges"]}) != len(document["edges"]):
        raise ValueError("Duplicate edge IDs")


def write_atomic(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    os.close(fd)
    temp = Path(temp_name)
    try:
        temp.write_text(payload, encoding="utf-8")
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--region", default="R02")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    document = build_export(args.baseline, args.graph, args.region)
    write_atomic(args.output, document)
    counts = {name: len(document[name]) for name in ("rooms", "edges", "doors", "npcs", "items", "spawns", "modifiers")}
    print(json.dumps({"output": str(args.output), "sha256": sha256_file(args.output), "counts": counts,
                      "primary_rooms": len(document["fixture"]["primary_room_ids"]), "stub_rooms": len(document["fixture"]["stub_room_ids"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
