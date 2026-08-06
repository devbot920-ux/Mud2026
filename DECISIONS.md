# Decision Log

## D-001 — Recover data before choosing an engine

- Date: 2026-08-02
- Status: Accepted

The canonical content pipeline will remain independent of Godot, Unity, Three.js, or other presentation technology. Engine evaluation begins only after a representative golden dataset is available.

## D-002 — Canonical semantic storage will be SQLite

- Date: 2026-08-02
- Status: Accepted provisionally

Use SQLite for normalized semantic data, integrity checks, and provenance. JSON will be a versioned export format. This can be revisited if Phase 1 reveals a concrete incompatibility.

## D-003 — Original sources remain external and immutable

- Date: 2026-08-02
- Status: Accepted

The repository stores tools, documentation, schemas, and tests. Original binaries and databases remain outside Git and are referenced through ignored local configuration. Tools must treat configured inputs as read-only.

## D-004 — Preserve uncertainty explicitly

- Date: 2026-08-02
- Status: Accepted

Decoded facts carry provenance and confidence. Unknown records and bytes are preserved. Inferences, manual overrides, and presentation-derived values must not masquerade as source facts.

## D-005 — Use GitHub Issues plus repository-local handoffs

- Date: 2026-08-02
- Status: Accepted

GitHub Issues will track complete actionable work once populated. `PROJECT_STATUS.md` and `BACKLOG.md` remain the authoritative quick-start context for fresh agents and offline work.

## D-006 — Use only the Python standard library for Phase 0 tooling

- Date: 2026-08-02
- Status: Accepted

The source inventory and its tests require no third-party packages, minimizing setup and making provenance capture reproducible on a normal Python installation.

## D-007 — Treat the Phase 2 graph audit as a provisional baseline

- Date: 2026-08-02
- Status: Accepted

Phase 2 may analyze the existing `graph.json` before Phase 1 is complete, but its topology, flags, regions, and coordinates remain derived evidence. Structural categories do not assert whether asymmetric connections are intentional. Phase 1 must regenerate and reconcile the topology before these findings can be promoted to source-backed facts.

## D-008 — Use Pendelhaven as the leading golden-fixture candidate

- Date: 2026-08-02
- Status: Accepted provisionally

Pendelhaven (`R02`) ranks first because its 60 rooms exercise doors, hidden and vertical connections, transports, stores, a tavern, a quest, spawns, and cross-region links while remaining much smaller than Imperial City. The final room subset will be selected after Phase 1 establishes canonical data.

## D-009 — Preserve raw SQLite content cell by cell

- Date: 2026-08-02
- Status: Accepted

The canonical baseline stores every source schema object, row, and value with its original SQLite storage class. BLOBs remain complete, and source files, rows, and values receive SHA-256 fingerprints. Decoded entities and fields are additive views with source-row, byte-offset, rule, and confidence evidence; they never replace raw records.

## D-010 — Prefer source-decoded multiedges over the legacy graph

- Date: 2026-08-02
- Status: Accepted

The legacy graph contains 7,077 edges and is lossy. Phase 1 recovers all of them plus 20 additional edges: 19 were suppressed by one-target-per-direction behavior, and one was suppressed when NetworkX `DiGraph` collapsed two directions sharing the same endpoints. The canonical topology retains all 7,097 source-decoded edges; future audits and renderers must support multiedges.

## D-011 — Canonical metrics supersede graph-only topology metrics

- Date: 2026-08-02
- Status: Accepted

Connectivity, reachability, and asymmetry decisions will use all 7,097 Phase 1 topology edges. The earlier 7,077-edge graph-only audit remains a useful record of legacy-export loss but is no longer authoritative for topology metrics. Derived regions, coordinates, and feature flags remain presentation evidence because they do not yet have a canonical source-backed equivalent.

## D-012 — Treat DLL modification consumers as tag evidence, not a field specification

- Date: 2026-08-02
- Status: Accepted

Calls to `_ACQUIRE_MODIFICATION(object, tag)` provide strong evidence that a numeric MOD1 tag participates in the surrounding gameplay function. A specific consumer can support a tag-family name, but decompiled names and control flow do not by themselves establish every field's meaning. Phase 3 therefore records function and line provenance, preserves byte variability, and leaves fields or tags unresolved unless corroborated.

## D-013 — MOD1 tags are little-endian 16-bit values

- Date: 2026-08-03
- Status: Accepted

Decode the MOD1 modification tag as a little-endian `u16` at raw offsets 8–9. The previous one-byte interpretation collapsed distinct high tags into low-byte families, including `0x0432` into item tag `0x0032` and `0x0430` into spawn tag `0x0030`. All catalogs, entity selection, fixture modifiers, provenance widths, and DLL correlations must retain the full 16-bit value. The corrected snapshot has 118 tags, 529 item bases, and 333 spawn records.

## D-013 — Bound the golden fixture by derived Pendelhaven membership plus one-hop stubs

- Date: 2026-08-02
- Status: Accepted

The fixture includes all 60 rooms assigned to derived region `R02` and every canonical topology edge touching one of them. External endpoints `416`, `958`, and `4061` are skeletal non-expanding stubs. This preserves inbound, outbound, hidden, and vertical boundary behavior without recursively importing neighboring regions. Region membership remains labeled as derived evidence.

## D-014 — Version the engine-neutral export and keep generated content private

- Date: 2026-08-02
- Status: Accepted

The first contract is `mud2026.engine-neutral-world` version `1.0.0`, described by a tracked JSON Schema. Generated exports remain under ignored `var/exports/` pending an explicit licensing/content decision. Complete raw bytes are retained only for associated non-base modifiers so unresolved records survive the handoff; tracked files contain tools, schema, tests, and aggregate findings only.

## D-015 — Continue the sustained playable client in Three.js

- Date: 2026-08-06
- Status: Accepted

Hands-on feedback selected the web prototype as the most usable of the three engine spikes. Three.js is the active playable client. Godot and Unity remain reference implementations and fixture-validation examples; new gameplay/UI work targets `prototypes/web` unless this decision is revisited.

## D-016 — Separate recovered Rose concepts from prototype balancing

- Date: 2026-08-06
- Status: Accepted

Character creation and UI terminology will follow recovered HEL1 evidence: six races, six starting walks of life, eight attributes, and prime-requisite proficiencies. Until original formulas and exact record fields are decoded, numerical race/walk modifiers, derived-stat formulas, starter skills, loot weights, and bonuses remain deterministic prototype rules. They must be tested and labeled as such rather than presented as recovered facts.
