# Mud2026

Mud2026 is a private research and development project to recover the data model of Rose COG and eventually present its text-based world as a graphical game.

The project is deliberately engine-neutral during data discovery. Godot, Unity, browser-based 3D, or another renderer can be evaluated after the source data is reproducibly decoded into a canonical format.

## Current stage

Phases 0–5 are implemented through the engine-comparison stage. Phase 1 provides a reproducible raw-provenance baseline, Phase 2 audits all 7,097 canonical edges, Phase 3 catalogs all 118 MOD1 tags, Phase 4 exports a closed Pendelhaven fixture, and Phase 5 loads that same corrected export in Godot, Unity, and Three.js prototypes. See [PROJECT_STATUS.md](PROJECT_STATUS.md), [docs/GOLDEN_FIXTURE_EXPORT.md](docs/GOLDEN_FIXTURE_EXPORT.md), and [docs/ENGINE_PROTOTYPE_COMPARISON.md](docs/ENGINE_PROTOTYPE_COMPARISON.md).

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

8. Export and inspect the private Pendelhaven fixture:

   ```powershell
   python scripts/export_golden_fixture.py
   python scripts/serve_fixture_viewer.py
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
- `viewer/` — engine-neutral private-export inspector
- `prototypes/` — comparable Godot, Unity, and Three.js playable-client spikes
