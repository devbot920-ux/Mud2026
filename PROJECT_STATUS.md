# Project Status

Updated: 2026-08-03
Branch: `dev`
Milestone: Phase 5 — corrected Pendelhaven engine prototypes in progress

## Current state

The repository foundation and provenance policy are established. The game engine remains intentionally undecided while the source data is recovered into an engine-neutral model.

Phase 1 imports every row and value from all 13 source databases into a reproducible raw-provenance SQLite baseline. Phase 2 audits all 7,097 source-decoded edges. Phase 3 catalogs all 118 MOD1 tags. Phase 4 defines an engine-neutral versioned JSON contract and closes the 60-room Pendelhaven fixture over topology, spawns, referenced entities, and modifiers. A 2026-08-03 correction promoted the MOD1 tag from one byte to little-endian `u16`, separating several previously collapsed high tags before Phase 5 client work.

Known source evidence:

- Decompiled DLL/project: `C:\temp\decompileproject\decomp2`
- Existing derived graph: `C:\temp\DoorTelnet\graph.json`
- Converted Btrieve/SQLite databases: `C:\dos\modules\*.db`
- Existing research scripts: `C:\temp\phyton\*.py`

Initial read-only analysis found:

- 3,446 unique rooms and 7,077 directed connections
- 22 derived/named regions
- 529 item keys represented by exactly 529 base-item records
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
- Canonical adapter and comparison audit at `scripts/audit_canonical_topology.py`
- Canonical report at `docs/CANONICAL_TOPOLOGY_AUDIT.md`
- Source-row and byte-offset provenance for all 20 edges omitted by the legacy graph
- Complete metric comparison showing how recovered multiedges change components and reachability

## Phase 1 deliverables

- Canonical raw-provenance schema at `schema/baseline.sql`
- Read-only, atomic, deterministic importer at `scripts/baseline_import.py`
- Complete preservation of SQLite schema objects, rows, storage classes, values, BLOBs, and hashes
- Catalog of all 118 MOD1 tag values without discarding unknown records
- Provisional DES1 plus known MOD1 room, door, item, NPC, spawn, trainer, promotion, spell-count, quest, and feature decoding with offsets/confidence
- Semantic topology reconciliation reproducing all 3,446 published rooms and all 7,077 published edges
- Preservation and explanation of 20 additional source-decoded edges omitted by the lossy graph builder

## Phase 3 deliverables

- Deterministic standard-library MOD1 evidence analyzer at `scripts/analyze_mod1_tags.py`
- Complete 118-tag evidence ledger and ranked 77-tag unresolved queue
- Same-key room, door, NPC, and item association plus tag co-occurrence analysis
- Per-offset byte-variability profiles without publishing source descriptions
- Decompiled `_ACQUIRE_MODIFICATION` correlation with function and line provenance
- Strong tag-family hypotheses for NPC extra attacks, armor-defense eligibility, trap events, limited shop stock, and conditional combat modifiers
- Tentative hypotheses for door strength/key rules and disease/poison effect slots
- Tracked concise report at `docs/MOD1_TAG_CATALOG.md`; detailed report remains under ignored `var/`

## Phase 4 deliverables

- Exact `R02` boundary: 60 primary rooms plus skeletal stubs `416`, `958`, and `4061`
- All 125 internal and 5 crossing canonical directed multiedges
- Versioned `mud2026.engine-neutral-world` `1.0.0` JSON Schema
- Deterministic read-only exporter at `scripts/export_golden_fixture.py`
- Complete closure over 2 door sides, 19 spawns, 32 spawn entries, 18 NPCs, 12 items, and 70 non-base modifiers
- Field, edge, entity, and modifier source-row provenance, confidence, and offsets
- Complete private raw bytes for 49 unresolved and 21 interpreted/hypothesized modifiers
- Minimal engine-neutral browser viewer at `viewer/index.html`
- Tracked report at `docs/GOLDEN_FIXTURE_EXPORT.md`; generated source content remains under ignored `var/exports/`

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
- Corrected baseline SHA-256 — `8FCACE1AA6936C0FAA487F3B0153B3EC82C707CB7D10B4E209050EFAE3C916ED`
- Corrected semantic digest — `75A631DA62158CECD3CF692AF9709712F3C47546211C9CDD923E5FE61CE69330`
- Reconciliation — zero missing/extra nodes, zero missing published edges, 20 additional source-decoded edges

Canonical Phase 2 verification completed on 2026-08-02:

- `python -m unittest discover -s tests -q` — 27 tests passed
- `python scripts/audit_canonical_topology.py` — 3,446 rooms, 7,097 edges, 189 missing reverse counterparts
- Integrity — zero duplicate IDs/logical edges, dangling edges, or unknown directions
- Connectivity — 49 weak components, 63 strong components, and 3,383 rooms reachable from seed room 1
- Recovered-edge effect — one fewer weak component, 16 fewer strong components, and 465 more rooms reachable from seed
- Repeated canonical-audit SHA-256 — `A12DCDADDEE3ED057E7D5956F4A13CE9C5DD19E4D87BBA9A990C1BD094F27179`
- Pendelhaven (`R02`) remains the leading golden-fixture candidate

Phase 3 verification completed on 2026-08-02:

- `python -m unittest discover -s tests -v` — 30 tests passed
- `python scripts/analyze_mod1_tags.py` — 7,060 records, 118 tags, 41 interpreted/hypothesized, 77 unresolved
- Corrected detailed-report SHA-256 — `82650E575D9BE827FFBBDB029DDB95079886C3B5681A49720269017103CD1A02`
- All source databases and the decompiled DLL were opened read-only
- Detailed evidence report includes no source description text

Phase 4 verification completed on 2026-08-02:

- `python -m unittest discover -s tests -v` — 36 tests passed
- `python scripts/export_golden_fixture.py` — 60 primary rooms, 3 stubs, 130 edges, 2 doors, 19 spawns, 18 NPCs, 12 items, 70 modifiers
- Corrected export SHA-256 — `146D19341A7172EFA604E7E32D9277A9E86750ADE26D5637CFDA1EDBBDDE2DA4`
- Referential integrity — zero dangling room-edge, NPC-spawn, or item-spawn references
- All source databases and the canonical baseline remained read-only
- `git diff --check` — passed before commit

## Unresolved questions

- What are the exact byte-field layouts within the newly classified MOD1 tag families?
- What are the semantic roles of INS1, ACT1, NAM1, RAND, SPEL, and HEL1 records?
- Which structurally asymmetric connections are intentional rather than extraction artifacts?
- Region assignments remain derived and are not yet present in the canonical source-backed model.
- The fixture's 49 unresolved modifiers still lack semantic meanings and field layouts.
- The generated export remains private pending a licensing/content decision.

## Exact next task

Begin Phase 5 by defining evaluation criteria and loading the unchanged Pendelhaven `1.0.0` export into leading 3D engine candidates. Continue decoding ranked MOD1 unknowns when playable fixture behavior requires them.
