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

- [ ] Define the raw provenance SQLite schema
- [ ] Import all SQLite metadata, keys, and BLOB records read-only
- [ ] Preserve full raw BLOBs and calculate per-record SHA-256
- [ ] Port DES1 decoding into tested modules
- [ ] Port known MOD1 decoding into tested modules
- [ ] Generate a machine-readable record-tag frequency catalog
- [ ] Compare regenerated rooms and edges with the current graph
- [ ] Explain every baseline count difference

## Phase 2 — World topology audit

- [ ] Classify 169 edges without reverse counterparts
- [ ] Audit connected components and unreachable rooms
- [ ] Audit door pairs, hidden exits, vertical links, portals, and transports
- [ ] Separate inferred region/layout data from original facts
- [ ] Select a varied golden fixture region

## Research queue

- [ ] Decode high-frequency unknown MOD1 tags
- [ ] Trace DLL Btrieve access and gameplay functions to record fields
- [ ] Decode INS1, SPEL, ACT1, NAM1, HEL1, and RAND
- [ ] Determine why 549 item-base records map to 529 item keys
