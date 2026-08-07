# Project Status

Updated: 2026-08-06
Branch: `dev`
Milestone: Phase 6 — Three.js sustained playable client underway

## Current state

The repository foundation and provenance policy are established. The game engine remains intentionally undecided while the source data is recovered into an engine-neutral model.

Phase 1 imports every row and value from all 13 source databases into a reproducible raw-provenance SQLite baseline. Phase 2 audits all 7,097 source-decoded edges. Phase 3 catalogs all 118 MOD1 tags. Phase 4 defines an engine-neutral versioned JSON contract and closes the 60-room Pendelhaven fixture over topology, spawns, referenced entities, and modifiers. A 2026-08-03 correction promoted the MOD1 tag from one byte to little-endian `u16`, separating several previously collapsed high tags before Phase 5 client work.

Phase 5 produced comparable Godot 4.7.1, Unity 6000.5.6f1, and Three.js clients loading the same corrected fixture. Hands-on feedback selected Three.js for the sustained playable client; Godot and Unity remain reference implementations.

The web client now has a source-aligned character/inventory slice. Character creation offers all six HEL1 races and starting walks of life. It models all eight recovered attributes, six foundational proficiencies with prime-attribute adjustment, health, movement, mana, attack delay, encumbrance, weighted inventory, and one weapon/one armor slot. Graphical Pack and Character menus coexist with command equivalents, and an explicit Commands/Mouse control switches cleanly between pointer-look and text entry. Exact numeric formulas and item values remain labeled prototype balancing pending deeper decoding.

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

## Phase 5 deliverables

- Equivalent code-driven room-stage prototypes under `prototypes/godot`, `prototypes/unity`, and `prototypes/web`
- Strict corrected-fixture validation in all three clients
- First-person movement, canonical edge portals, text commands, room UI, spawn placeholders, hidden toggle, and developer overlay
- Godot headless/editor runtime verification with 15 assertions
- Unity 5/5 EditMode verification and successful Windows x64 development build
- Three.js 10/10 tests, production Vite build, zero npm audit findings, and real-browser travel smoke test
- Tracked evaluation at `docs/ENGINE_PROTOTYPE_COMPARISON.md`

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

Phase 5 verification completed on 2026-08-03:

- Shared Python suite — 36/36 tests passed
- Godot 4.7.1 — 15/15 fixture assertions, editor import, and headless runtime passed
- Unity 6000.5.6f1 — 5/5 EditMode tests passed; Windows x64 development build succeeded at approximately 148.5 MB
- Three.js — 10/10 tests, TypeScript check, Vite production build, and browser travel smoke passed
- Three.js dependency audit — zero known vulnerabilities; production JavaScript 492.15 kB / 124.98 kB gzip
- All three clients consumed the unchanged corrected fixture; generated builds and private source content remain ignored
- `git diff --check` — passed

Phase 6 RPG-interface verification completed on 2026-08-06:

- Read-only HEL1 inspection recovered race, walk-of-life, attribute, proficiency, equipment, delay, mana, health, armor, and encumbrance help concepts
- Decompiled DLL consumers corroborate inventory lists, equipped slots, wear checks, and current/maximum encumbrance
- Three.js Vitest suite — 73/73 tests passed across 9 files
- TypeScript check and Vite production build — passed
- Automated localhost browser control was blocked by browser URL policy; no bypass was attempted

Phase 6 combat/casting verification completed on 2026-08-06:

- Read-only `RCI_SPEL.db` inspection decoded and privately exported all 97 fixed-width spell records
- Decompiled DLL traces recovered d100 casting success, mana consumption, sphere proficiency deltas, inclusive spell damage dice, level-scaled healing dice, and bounded base recovery delay
- The client now includes class starter spellbooks, casting UI/commands, mana/recovery, failure, spell damage, healing, proximity action buttons, range-based combat, hostile chase, exit blocking, sprint/flee escape, and eligible room-to-room pursuit
- Melee now uses the confirmed proficiency/requirement, d100, armor, over-encumbrance, and damage-range structure; exact weapon record values remain explicit prototype balancing
- Three.js Vitest suite — 83/83 tests passed across 11 files
- Shared Python suite — 38/38 tests passed, including synthetic fixed-width spell decoding
- TypeScript check and Vite production build — passed
- Automated localhost browser control remained blocked by browser URL policy; no bypass was attempted

Phase 6 character-progression verification completed on 2026-08-07:

- HEL1 and DLL traces recovered explicit promotion, `50 + current-level d10` development-point grants, 2 attribute points, trainer-bound spending, the Warrior/Melee 3-point example, and resting state transitions
- All 175 decoded armor records correlate wearable-location byte 73 to 12 locations; the client renders all 12 plus the separate weapon slot
- Experience is banked until `PROMOTE` in Pendlehaven Guild, whose fixture modifier caps promotion at level 5
- Oscar provides proximity-gated proficiency and attribute spending; exact silver and specialized-trainer rules remain pending the economy
- Strength and trained attributes now feed physical damage and adjusted proficiency; REST restores resources until interrupted
- Three.js Vitest suite — 87/87 tests passed across 11 files
- TypeScript check — passed

Phase 6 encounter-lifecycle verification completed on 2026-08-07:

- Read-only DLL and NPC-record inspection recovered behavior 1 as scan/engage-any-player, behavior 2 as criminals-only, and target tracking after engagement
- Giant slug 4003, kobold 129, kobold thug 4004, and kobold guard 4006 all carry behavior 1 and now auto-engage after a short entry grace period
- Defeated models and interactions are removed immediately; prototype equipment rewards become persistent ground objects with mouse/proximity/command pickup
- World respawning is keyed to the original spawn room, uses a provisional two-minute cooldown, and occurs only on a subsequent room build
- Three.js Vitest suite — 91/91 tests passed across 12 files
- TypeScript check and Vite production build — passed

## Unresolved questions

- What are the exact byte-field layouts within the newly classified MOD1 tag families?
- What are the semantic roles of INS1, ACT1, NAM1, RAND, SPEL, and HEL1 records?
- Which structurally asymmetric connections are intentional rather than extraction artifacts?
- Region assignments remain derived and are not yet present in the canonical source-backed model.
- The fixture's 49 unresolved modifiers still lack semantic meanings and field layouts.
- The generated export remains private pending a licensing/content decision.

## Exact next task

Hands-on enter each current hostile room, verify automatic pursuit, kill one mob, confirm its model cannot be attacked again, leave its reward on the floor across a room round-trip, then collect it by both proximity and command in separate runs. Next decode exact corpse/respawn/drop fields, item damage/requirements, training tables, and additional spell handlers, then implement shops/currency and private save-state persistence.
