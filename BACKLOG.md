# Backlog

The complete future tracker will be GitHub Issues. This file keeps the immediate ordered queue available to fresh agents.

## Phase 0 — Project foundation

- [x] Establish repository on `dev`
- [x] Add operating and handoff documentation
- [x] Define source-data and uncertainty policies
- [x] Add ignored local source configuration
- [x] Add deterministic SHA-256 source inventory
- [x] Add Phase 0 automated tests
- [ ] Create GitHub labels and milestones when GitHub issue tooling is available

## Phase 1 — Reproducible baseline import

- [x] Define the raw provenance SQLite schema
- [x] Import all SQLite metadata, keys, and BLOB records read-only
- [x] Preserve full raw BLOBs and calculate per-record SHA-256
- [x] Port DES1 decoding into tested modules
- [x] Port known MOD1 decoding into tested modules
- [x] Generate a machine-readable record-tag frequency catalog
- [x] Compare regenerated rooms and edges with the current graph
- [x] Explain every baseline count difference

## Phase 2 — World topology audit

- [x] Structurally classify 169 edges without reverse counterparts
- [x] Audit connected components and unreachable rooms
- [x] Audit door pairs, hidden exits, vertical links, portals, and transports
- [x] Separate inferred region/layout data from original facts
- [x] Select Pendelhaven (`R02`) as the leading golden-fixture region
- [x] Recompute and reconcile Phase 2 metrics against all 7,097 canonical edges

## Phase 3 — Record-type reverse engineering

- [x] Generate a ranked unknown-tag research catalog with representative source-row IDs
- [x] Correlate high-frequency MOD1 tags with entity keys and known modifiers
- [x] Trace DLL modification lookups to tag hypotheses and field-research leads
- [x] Decode and test initial gameplay-critical NPC and item tag families
- [x] Decode initial door/lock, store, quest, combat, and behavior tag families
- [x] Record evidence and confidence for every tag; preserve 77 unresolved tags

## Phase 4 — Golden fixture and export contract

- [x] Select the exact Pendelhaven room boundary and required cross-region stubs
- [x] Define a versioned engine-neutral JSON export schema
- [x] Export fixture rooms, multiedges, doors, NPCs, items, spawns, and decoded modifiers
- [x] Add referential-integrity and deterministic-output tests
- [x] Produce a minimal engine-neutral data viewer before choosing the 3D engine

## Phase 5 — Engine evaluation spike

- [ ] Define renderer evaluation criteria against the Pendelhaven fixture
- [ ] Prototype fixture loading in the leading engine candidates without changing the export contract
- [ ] Compare navigation, asset pipeline, AI-assisted iteration, deployment, and maintenance cost
- [ ] Select the first playable-client engine and record the decision

## Research queue

- [ ] Decode the ranked high-frequency unknown MOD1 tags
- [ ] Trace DLL consumers from tag-level meanings to exact record fields
- [ ] Decode INS1, SPEL, ACT1, NAM1, HEL1, and RAND
- [x] Resolve the apparent 549/529 item mismatch as a one-byte tag-decoding collision (`0x0032` versus `0x0432`)
