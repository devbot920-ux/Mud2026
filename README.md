# Mud2026

Mud2026 is a private research and development project to recover the data model of Rose COG and eventually present its text-based world as a graphical game.

The project is deliberately engine-neutral during data discovery. Godot, Unity, browser-based 3D, or another renderer can be evaluated after the source data is reproducibly decoded into a canonical format.

## Current stage

Phases 0–3 are complete. Phase 1 provides a reproducible raw-provenance baseline, Phase 2 audits all 7,097 canonical edges, and Phase 3 catalogs all 113 MOD1 tags with evidence while preserving 72 unresolved meanings. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the current handoff, [docs/BASELINE_IMPORT.md](docs/BASELINE_IMPORT.md) for Phase 1, [docs/CANONICAL_TOPOLOGY_AUDIT.md](docs/CANONICAL_TOPOLOGY_AUDIT.md) for Phase 2, [docs/MOD1_TAG_CATALOG.md](docs/MOD1_TAG_CATALOG.md) for Phase 3, and [BACKLOG.md](BACKLOG.md) for the ordered queue.

## Safety and data ownership

Original databases, DAT files, decompiled binaries, generated private manifests, and other potentially copyrighted source material are not committed. Tools read source locations configured in `config/source_paths.local.json`; they must never modify those locations.

## Quick start

1. Copy `config/source_paths.example.json` to `config/source_paths.local.json` and adjust paths if necessary.
2. Generate a private source inventory:

   ```powershell
   python scripts/inventory_sources.py
   ```

3. Run the standard-library test suite:

   ```powershell
   python -m unittest discover -s tests -v
   ```

4. Run the provisional topology audit:

   ```powershell
   python scripts/audit_topology.py
   ```

5. Build the ignored canonical baseline and reconciliation report:

   ```powershell
   python scripts/baseline_import.py
   ```

6. Audit and compare the canonical topology:

   ```powershell
   python scripts/audit_canonical_topology.py
   ```

7. Build the MOD1 evidence catalog:

   ```powershell
   python scripts/analyze_mod1_tags.py
   ```

The inventory is written to `var/manifests/source-manifest.json`, which Git ignores because it contains local paths and fingerprints of private inputs.

## Repository map

- `AGENTS.md` — mandatory operating instructions for fresh agents
- `PROJECT_STATUS.md` — concise current-state handoff
- `DECISIONS.md` — durable architectural decisions
- `DATA_DICTIONARY.md` — decoded entities, fields, tags, and confidence
- `BACKLOG.md` — immediate offline task queue
- `config/` — example and ignored local source-path configuration
- `docs/` — conventions and research documentation
- `scripts/` — reproducible read-only tooling
- `tests/` — automated validation
