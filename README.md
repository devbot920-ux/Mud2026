# Mud2026

Mud2026 is a private research and development project to recover the data model of Rose COG and eventually present its text-based world as a graphical game.

The project is deliberately engine-neutral during data discovery. Godot, Unity, browser-based 3D, or another renderer can be evaluated after the source data is reproducibly decoded into a canonical format.

## Current stage

Phases 0 and 1 are complete. Phase 1 provides a reproducible raw-provenance baseline and recovers all published topology plus 20 edges omitted by the legacy graph builder. Phase 2's original derived-graph audit is complete, with a canonical-edge re-audit pending. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the current handoff, [docs/BASELINE_IMPORT.md](docs/BASELINE_IMPORT.md) for Phase 1, [docs/TOPOLOGY_AUDIT.md](docs/TOPOLOGY_AUDIT.md) for Phase 2, and [BACKLOG.md](BACKLOG.md) for the ordered work queue.

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
