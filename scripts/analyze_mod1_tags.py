#!/usr/bin/env python3
"""Build an evidence-led catalog of every RCI_MOD1 tag without mutating sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "var" / "baseline" / "rose-baseline.sqlite"
DEFAULT_DLL = Path(r"C:\temp\decompileproject\decomp2\RCIROSE.DLL.c")
DEFAULT_JSON = ROOT / "var" / "reports" / "mod1-tag-analysis.json"
DEFAULT_MARKDOWN = ROOT / "docs" / "MOD1_TAG_CATALOG.md"

# Meanings already established by Phase 1, plus Phase 3 hypotheses whose DLL
# call sites are sufficiently specific. Confidence describes meaning, not fields.
KNOWN: dict[int, tuple[str, str, str]] = {
    0x0A:("room","strong","Phase 1 topology reconciliation"),
    0x0D:("door","strong","Phase 1 topology reconciliation"),
    0x28:("npc","strong","Phase 1 identity reconciliation"),
    0x30:("spawn","strong","Phase 1 decoding"),
    0x32:("item","strong","Phase 1 identity reconciliation"),
    0x33:("weapon","strong","weapon and combat DLL consumers"),
    0x34:("armor","strong","armor, AC, defense-pool, and wear DLL consumers"),
    0x37:("store","strong","shop-item DLL consumer and Phase 1 decoding"),
    0x48:("skill_trainer","strong","Phase 1 decoding"),
    0x5D:("door_strength_or_key_rule","tentative","PICKSTRENGTH, DOORSTRENGTH, and STEALSKEY consumers"),
    0x6D:("peaceful","tentative","Phase 1 decoding"),
    0x6E:("spell_count","tentative","Phase 1 decoding"),
    0x72:("tavern","tentative","Phase 1 decoding"),
    0x75:("promotion","tentative","Phase 1 decoding"),
    0x85:("attribute","tentative","Phase 1 decoding"),
    0xB2:("armor_defense_eligibility","strong","GET_AC, GET_AC2, and GET_DPOOL consumers"),
    0xC5:("quest","tentative","Phase 1 decoding"),
    0xCC:("potion","strong","QUAFF DLL consumer and Phase 1 decoding"),
    0xE0:("trap","tentative","Phase 1 decoding"),
    0xE1:("trap_event_component_1","strong","DO_TRAP_EVENTS consumer"),
    0xE2:("trap_event_component_2","strong","DO_TRAP_EVENTS consumer"),
    0xE3:("trap_event_component_3","strong","DO_TRAP_EVENTS consumer"),
    0xE4:("limited_shop_stock","strong","LIMITED_AVAILABLE, PC_BUYITEM, and shop-stock consumers"),
    0xEE:("conditional_combat_modifier_1","strong","bane to-hit, AC, defense-pool, damage multiplier consumers"),
    0xEF:("conditional_combat_modifier_2","strong","bane to-hit, AC, defense-pool, damage multiplier consumers"),
    0xF0:("conditional_combat_modifier_3","strong","bane to-hit, AC, defense-pool, damage multiplier consumers"),
}
for tag, direction in zip(range(0xA6, 0xB0), ("north","northeast","east","southeast","south","southwest","west","northwest","up","down")):
    KNOWN[tag] = (f"hidden_exit_{direction}", "strong", "Phase 1 topology reconciliation")
for tag in range(0x76, 0x7E):
    KNOWN[tag] = (f"npc_extra_attack_slot_{tag-0x75}", "strong", "NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers")
for tag in range(0x8A, 0x94):
    KNOWN[tag] = (f"disease_effect_slot_{tag-0x89}", "tentative", "disease-test/cure/death-clear consumers")
for tag in range(0x94, 0x9E):
    KNOWN[tag] = (f"poison_effect_slot_{tag-0x93}", "tentative", "poison-test/antidote/cure/death-clear consumers")

FUNCTION_RE = re.compile(r"^[A-Za-z_].*\b(_[A-Z][A-Z0-9_]*)\s*\(")
CALL_RE = re.compile(r"_ACQUIRE_MODIFICATION\s*\([^\n]*?,\s*(0x[0-9a-fA-F]+|\d+)\s*\)")
PRIORITY_WORDS = ("NPC", "ATTACK", "AC", "DPOOL", "DOOR", "SHOP", "BUY", "QUEST", "ITEM", "TRAP", "POISON", "DISEASE")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_mod1(path: Path) -> list[dict[str, Any]]:
    uri = path.resolve().as_uri() + "?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        rows = connection.execute("""
          SELECT r.source_row_id,
                 max(CASE WHEN v.column_name='key_0' THEN v.integer_value END),
                 max(CASE WHEN v.column_name='key_1' THEN v.integer_value END),
                 max(CASE WHEN v.column_name='data' THEN v.blob_value END)
          FROM source_row r JOIN source_file f USING(source_file_id)
          JOIN source_value v USING(source_row_id)
          WHERE f.logical_name='RCI_MOD1' AND r.table_name='data_t'
          GROUP BY r.source_row_id ORDER BY r.source_row_id
        """).fetchall()
    finally:
        connection.close()
    result = []
    for source_row_id, key_0, key_1, data in rows:
        if not isinstance(data, bytes) or len(data) < 10:
            raise ValueError(f"MOD1 source row {source_row_id} has no little-endian u16 tag at offsets 8..9")
        result.append({"source_row_id": source_row_id, "key_0": key_0, "key_1": key_1, "data": data, "tag": int.from_bytes(data[8:10], "little")})
    return result


def dll_calls(path: Path) -> dict[int, list[dict[str, Any]]]:
    calls: dict[int, list[dict[str, Any]]] = defaultdict(list)
    function = "<global>"
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = FUNCTION_RE.match(line)
        if match:
            function = match.group(1)
        for call in CALL_RE.finditer(line):
            tag = int(call.group(1), 0)
            calls[tag].append({"function": function, "line": number})
    return dict(calls)


def analyze(rows: list[dict[str, Any]], calls: dict[int, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    by_tag: dict[int, list[dict[str, Any]]] = defaultdict(list)
    key_tags: dict[int, set[int]] = defaultdict(set)
    for row in rows:
        by_tag[row["tag"]].append(row)
        key_tags[row["key_0"]].add(row["tag"])
    catalog = []
    anchors = {0x0A:"room", 0x0D:"door", 0x28:"npc", 0x32:"item"}
    for tag in sorted(by_tag):
        group = by_tag[tag]
        functions = Counter(call["function"] for call in calls.get(tag, []))
        associations = Counter()
        cooccurrence = Counter()
        for row in group:
            present = [name for anchor, name in anchors.items() if anchor in key_tags[row["key_0"]]]
            associations.update(present or ["unanchored"])
            cooccurrence.update(key_tags[row["key_0"]] - {tag})
        lengths = Counter(len(row["data"]) for row in group)
        max_len = max(lengths)
        unique_by_offset = [len({row["data"][offset] for row in group if len(row["data"]) > offset}) for offset in range(max_len)]
        known = KNOWN.get(tag)
        score = len(group) + 100 * sum(any(word in name for word in PRIORITY_WORDS) for name in functions)
        catalog.append({
            "tag": f"0x{tag:04X}", "tag_decimal": tag,
            "status": "interpreted" if known else "unresolved",
            "name": known[0] if known else None,
            "confidence": known[1] if known else "unknown",
            "meaning_evidence": known[2] if known else "No semantic claim; retained for research.",
            "record_count": len(group), "distinct_key_0": len({r['key_0'] for r in group}),
            "record_lengths": {str(k): v for k, v in sorted(lengths.items())},
            "entity_key_associations": dict(sorted(associations.items())),
            "top_cooccurring_tags": [{"tag":f"0x{k:04X}","shared_keys":v} for k,v in cooccurrence.most_common(8)],
            "variable_offsets": [i for i, count in enumerate(unique_by_offset) if count > 1],
            "unique_values_by_offset": unique_by_offset,
            "dll_calls": calls.get(tag, []),
            "dll_function_counts": dict(sorted(functions.items())),
            "research_score": score,
            "representative_source_rows": [r["source_row_id"] for r in group[:3]],
        })
    return catalog


def build_report(baseline: Path, dll: Path) -> dict[str, Any]:
    rows = read_mod1(baseline)
    catalog = analyze(rows, dll_calls(dll))
    unresolved = sorted((x for x in catalog if x["status"] == "unresolved"), key=lambda x: (-x["research_score"], -x["record_count"], x["tag_decimal"]))
    return {
        "schema_version": 1,
        "sources": {"baseline":{"path":str(baseline.resolve()),"sha256":sha256_file(baseline)}, "decompiled_dll":{"path":str(dll.resolve()),"sha256":sha256_file(dll)}},
        "method": ["MOD1 little-endian u16 tag at offsets 8..9", "same-key entity anchor and co-occurrence analysis", "per-offset byte variability", "decompiled _ACQUIRE_MODIFICATION call-site correlation"],
        "counts": {"records":len(rows), "tags":len(catalog), "interpreted":sum(x["status"]=="interpreted" for x in catalog), "unresolved":len(unresolved)},
        "ranked_unresolved_tags": [x["tag"] for x in unresolved],
        "catalog": catalog,
        "limitations": ["Function names and decompiled control flow are evidence, not original symbols or a specification.", "A tag-level interpretation does not decode its fields.", "Same key_0 indicates association, not necessarily ownership.", "No source description text is copied into this report."],
    }


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    unresolved = [next(x for x in report["catalog"] if x["tag"] == tag) for tag in report["ranked_unresolved_tags"][:20]]
    promoted = [x for x in report["catalog"] if x["tag_decimal"] in set(range(0x76,0x7E))|set(range(0x8A,0x9E))|{0x5D,0xB2,0xE1,0xE2,0xE3,0xE4,0xEE,0xEF,0xF0}]
    lines = [
        "# MOD1 Tag Evidence Catalog", "",
        "Phase 3 catalogs every MOD1 tag and ranks unresolved work. It does not claim that every tag or field is decoded. The ignored JSON report retains per-tag provenance, byte variability, co-occurrence, and DLL call-site line numbers.", "",
        "## Coverage", "",
        f"- {counts['records']:,} records across {counts['tags']} tag values",
        f"- {counts['interpreted']} interpreted or hypothesized tags; {counts['unresolved']} explicitly unresolved",
        "- Source descriptions are excluded from both reports", "",
        "## Phase 3 promotions", "",
        "| Tag | Meaning | Confidence | Evidence |", "|---|---|---|---|",
    ]
    for item in promoted:
        lines.append(f"| `{item['tag']}` | `{item['name']}` | {item['confidence']} | {item['meaning_evidence']} |")
    lines += ["", "## Highest-priority unresolved tags", "", "| Rank | Tag | Records | Keys | Entity-key association | DLL consumers |", "|---:|---|---:|---:|---|---|"]
    for rank, item in enumerate(unresolved, 1):
        assoc = ", ".join(f"{k}:{v}" for k,v in item["entity_key_associations"].items())
        funcs = ", ".join(list(item["dll_function_counts"])[:4]) or "none found"
        lines.append(f"| {rank} | `{item['tag']}` | {item['record_count']} | {item['distinct_key_0']} | {assoc} | {funcs} |")
    lines += ["", "## Interpretation rules", "", "- `strong`: specific DLL consumers and/or an existing end-to-end reconciliation support the tag meaning.", "- `tentative`: evidence supports a family or role, but exact semantics remain uncertain.", "- `unknown`: no semantic name is assigned; records and evidence remain preserved.", "", "Field layouts remain unresolved unless separately documented. Re-run `python scripts/analyze_mod1_tags.py` after changing the baseline or adding evidence.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--dll", type=Path, default=DEFAULT_DLL)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    report = build_report(args.baseline, args.dll)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(report), encoding="utf-8")
    print(f"Cataloged {report['counts']['tags']} tags; {report['counts']['unresolved']} unresolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
