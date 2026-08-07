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

- [x] Define renderer evaluation criteria against the Pendelhaven fixture
- [x] Prototype the unchanged fixture in Godot, Unity, and Three.js
- [x] Compare navigation, asset pipeline, AI-assisted iteration, deployment, and maintenance cost
- [ ] Select the first playable-client engine and record the decision

## Phase 6 — First sustained playable client

- [ ] Run the documented hands-on comparison route in all three prototypes
- [x] Confirm Three.js as the primary playable client and retain the other clients as reference implementations
- [ ] Install matching export templates/modules for the selected deployment targets
- [ ] Add stateful doors and room interaction without changing canonical topology
- [x] Add a functional weighted inventory/equipment slice with explicit prototype-only item values
- [x] Add NPC interaction and spawning from evidence-backed fixture fields
- [x] Add graphical character, proficiency, inventory, and control-mode menus
- [x] Decode the initial SPEL record layout and integrate source-backed casting success, mana, damage, healing, and delays
- [x] Add proximity actions, in-room hostile pursuit, melee range, exit blocking, and eligible room-to-room pursuit
- [x] Integrate the recovered melee d100/proficiency/encumbrance structure with clearly provisional weapon-record values
- [x] Replace automatic leveling with explicit source-aligned promotion and promotion-room limits
- [x] Grant development/attribute points on promotion and require proximity to Oscar to spend them
- [x] Map all 12 source wearable-location codes, render every slot, and add the fixture's animal-hide boots
- [x] Add interruptible out-of-combat REST recovery
- [ ] Decode item weight, equipment-location, proficiency requirement, and restriction fields to replace prototype values
- [ ] Add shops, currency, buying/selling, and source-backed encumbrance penalties
- [ ] Decode exact walk/proficiency training tables and add the recovered silver cost after currency exists
- [ ] Add private save-state persistence separate from canonical source data

## Research queue

- [ ] Decode the ranked high-frequency unknown MOD1 tags
- [ ] Trace DLL consumers from tag-level meanings to exact record fields
- [ ] Decode INS1, ACT1, NAM1, HEL1, and RAND; continue SPEL targeting and non-damage handlers beyond the initial decoded layout
- [x] Resolve the apparent 549/529 item mismatch as a one-byte tag-decoding collision (`0x0032` versus `0x0432`)
