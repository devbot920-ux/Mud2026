# Project Status

Updated: 2026-08-02
Branch: `dev`
Milestone: Phase 1 — reproducible baseline import complete; canonical topology re-audit pending

## Current state

The repository foundation and provenance policy are established. The game engine remains intentionally undecided while the source data is recovered into an engine-neutral model.

Phase 1 now imports every row and value from all 13 source databases into a reproducible raw-provenance SQLite baseline. It also ports the legacy-understood DES1/MOD1 decoding with field-level evidence and reconciles the source-decoded topology against the derived graph. Phase 2 previously audited the derived graph; its metrics must now be recomputed against the 20 additional source-backed edges retained by Phase 1.

Known source evidence:

- Decompiled DLL/project: `C:\temp\decompileproject\decomp2`
- Existing derived graph: `C:\temp\DoorTelnet\graph.json`
- Converted Btrieve/SQLite databases: `C:\dos\modules\*.db`
- Existing research scripts: `C:\temp\phyton\*.py`

Initial read-only analysis found:

- 3,446 unique rooms and 7,077 directed connections
- 22 derived/named regions
- 529 item keys represented by 549 base-item records
- 211 NPC identities
- 4,398 DES1 description records
- More than 100 MOD1 record-tag values, most not yet semantically decoded

## Phase 0 deliverables

- Repository instructions and fresh-agent handoff files
- Architectural decisions, data dictionary, conventions, and backlog
- Ignored local source-path configuration
- Deterministic read-only SHA-256 inventory tool
- Standard-library tests for discovery, hashing, ordering, metadata, and output behavior
- Private local source manifest under ignored `var/`

## Phase 2 deliverables

- Deterministic, standard-library topology audit with detailed ignored JSON output
- Tracked concise report at `docs/TOPOLOGY_AUDIT.md`
- Integrity, component, reachability, reverse-link, special-topology, and derived-layout checks
- Explicit structural classification of all 169 missing reverse counterparts
- Auditable golden-fixture ranking selecting Pendelhaven (`R02`) as the leading candidate

## Phase 1 deliverables

- Canonical raw-provenance schema at `schema/baseline.sql`
- Read-only, atomic, deterministic importer at `scripts/baseline_import.py`
- Complete preservation of SQLite schema objects, rows, storage classes, values, BLOBs, and hashes
- Catalog of all 113 MOD1 tag values without discarding unknown records
- Provisional DES1 plus known MOD1 room, door, item, NPC, spawn, trainer, promotion, spell-count, quest, and feature decoding with offsets/confidence
- Semantic topology reconciliation reproducing all 3,446 published rooms and all 7,077 published edges
- Preservation and explanation of 20 additional source-decoded edges omitted by the lossy graph builder

## Evidence and verification

The inventory script opens files only for binary reading and writes only its configured manifest below the repository. Inputs are expanded deterministically and duplicate resolved files are rejected from duplicate output.

Phase 0 verification completed on 2026-08-02:

- `python -m unittest discover -s tests -v` — 6 tests passed
- `python scripts/inventory_sources.py` — 32 files, 19,822,399 bytes
- Repeated manifest SHA-256 — `E46795C7BB56FF02EB91F178512C4D10A03C3EB37897E2778EB0BC00BADD18B7` on both runs
- `git diff --check` — passed
- Git ignore checks confirmed the local path configuration and private manifest are excluded

Phase 2 verification completed on 2026-08-02:

- `python -m unittest discover -s tests -v` — 15 tests passed
- `python scripts/audit_topology.py` — 3,446 nodes, 7,077 edges, 169 missing reverse counterparts
- Derived graph SHA-256 — `C499A15CDDB7548D96914EE1E9571A876E9C388358A30F14FA52617F26202B24`
- Repeated detailed-report SHA-256 — `A02878D775C4E9F06C558D1B005097DC76E7137ACCC35494F57AD486FDA154D7`
- `git diff --check` — passed before commit

Phase 1 verification completed on 2026-08-02:

- `python -m unittest discover -s tests -q` — 23 tests passed
- Imported 13 databases, 97 schema objects, 16,720 rows, and 58,531 values
- Canonical baseline contains 9,069 decoded entities, 26,441 decoded fields, and 7,097 topology edges
- `PRAGMA integrity_check` — `ok`; `PRAGMA foreign_key_check` — zero violations
- Source-file hash comparison — zero mismatches
- Repeated baseline SHA-256 — `4AD060F062E6C052366B5BABCB1C3A95D6B6223D9CDE630EEF234D0E3CD82C8A`
- Semantic digest — `40D6E03DB1F44C70C848C5920D1D0BC9CC3FB7AEB0BC0839621565D21DA2A3EA`
- Reconciliation — zero missing/extra nodes, zero missing published edges, 20 additional source-decoded edges

## Unresolved questions

- Which MOD1 tags encode core NPC, item, combat, store, lock, and quest behavior?
- What are the semantic roles of INS1, ACT1, NAM1, RAND, SPEL, and HEL1 records?
- Which structurally asymmetric connections are intentional rather than extraction artifacts?
- How do the 20 source-backed edges omitted by `graph.json` change Phase 2 component, reachability, and asymmetry metrics?
- Region assignments remain derived and are not yet present in the canonical source-backed model.

## Exact next task

Re-run the Phase 2 topology analysis against the canonical Phase 1 edge set, compare its metrics with the derived-graph audit, and document the effect of the 20 recovered edges. Then begin systematic decoding of the remaining MOD1 tags.
