# Phase 1 Baseline Import

Phase 1 creates an engine-neutral, raw-provenance SQLite baseline without
writing to any source database. Run it from the repository root:

```powershell
python scripts/baseline_import.py
```

Generated, ignored outputs are `var/baseline/rose-baseline.sqlite` and
`var/reports/baseline-import.json`. Replacement is atomic. Inputs are opened
with SQLite URI `mode=ro`, `immutable=1`, and `PRAGMA query_only=ON`; hashes
are checked again after import.

## Raw preservation

The tracked schema is `schema/baseline.sql`. It records every `sqlite_master`
object and every row/value from every table in the 13 configured databases.
Each value keeps its SQLite storage class and complete value, including exact
BLOB bytes. TEXT byte lengths and hashes use its UTF-8 representation.
Source-file, row, and value SHA-256 hashes are retained. Row
identity JSON contains primary-key and `key_*` values plus a deterministic
source ordinal. Unknown databases, tables, columns, records, tags, and bytes
are not filtered out.

On the 2026-08-02 source snapshot the baseline contains:

- 13 source files; 16,720 rows; 58,531 values
- 97 schema objects (39 tables, 50 indexes, 8 triggers)
- 4,398 DES1 records (4,397 distinct embedded identifiers)
- 3,446 room-base, 78 door, 529 item-base, 211 NPC-base, and 333 spawn records
- 7,097 source-decoded topology edges: 7,017 base and 80 door

## Provisional decoding rules

All interpretations are ports of assumptions in
`C:\temp\phyton\02_secondrealtry.py`, not newly inferred meanings:

- MOD1 record tag: little-endian `u16` at byte offsets 8–9 (zero-based). The
  machine-readable catalog includes all 118 observed values. A short record is cataloged with a null
  tag; none are short in the current source snapshot.
- Embedded ID: little-endian u32 at offset 0 (`strong`).
- Short description: up to 50 bytes from offset 70, NUL-trimmed CP437
  (`tentative`).
- DES1: embedded little-endian u32 at offset 0, then leading-NUL removal and
  NUL-trimmed CP437 text (`tentative`). Both records sharing ID 100081 remain
  separate; no duplicate is discarded.
- Exits: ordinal direction bytes at offsets 170..179 correspond, in packed
  order, to little-endian u32 targets beginning at offset 30 (`tentative`).
- Hidden direction markers: MOD1 tags `0xA6` through `0xAF` (`tentative`).
- Items, NPCs, and rooms retain ID/description joins. Item category evidence
  (`0x33` weapon, `0x34` armor, `0xCC` potion) references each actual modifier
  row rather than the item-base row (`tentative`).
- Room feature flags are based only on the previously documented modifier-tag
  presence. Attribute (`0x85`) and skill (`0x48`) code/max/min use offsets
  70/71/72. Names are the legacy script's lookup labels; an unmapped code is
  preserved while its name is null. Promotion (`0x75`) maximum is offset 10,
  spell-trainer (`0x6E`) count is offset 220, and quest (`0xC5`) text begins at
  offset 70 and uses the legacy CP437 NUL-segment join rule (`tentative`).
- Spawn count is byte 221; up to eight u16 IDs begin at byte 10 and byte counts
  at byte 70. NPC/item classification is set membership; unmatched IDs remain
  `unknown` (`tentative`).

Every decoded field records its source row, byte offset/width where applicable,
rule, and confidence. Long descriptions remain only in the ignored database;
this tracked document does not reproduce them.

## Derived graph reconciliation

Comparison is semantic only: `(source, target, direction, door, hidden)`.
Coordinates and regions are intentionally excluded.

- Nodes: exact match, 3,446 generated and 3,446 in `graph.json`.
- Published edges: all 7,077 are reproduced; none are missing.
- The baseline retains 20 additional decoded edges.

Nineteen extras share a source and direction with another edge. The legacy
graph builder explicitly prefers a base exit over a door in the same direction
and stores one target per direction; this accounts for those omissions. The
remaining extra is room 2692 `W` to 2693: the graph also has `NW` to the same
target, and its NetworkX `DiGraph` representation keeps only one edge for a
source/target pair. Thus the count difference is explained by lossy derived
graph construction, not by a missing source record. Exact difference arrays
are in the generated JSON report.

## Verification and limits

The importer validates SQLite integrity, emits a representation-independent
semantic digest, and produces byte-identical SQLite output for identical
inputs on the current runtime. Tests cover full BLOB/schema preservation,
unknown and truncated tags, decoding provenance, source immutability,
idempotence, atomic failure, and truncated/unknown direction bytes.

Most of the 118 MOD1 tags and the semantic contents of INS1, ACT1, NAM1, HEL1,
RAND, and SPEL remain undecoded. Raw preservation makes future decoding
additive without requiring another conversion from the original databases.
