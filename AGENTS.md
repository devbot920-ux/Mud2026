# Agent Instructions

These instructions apply to the entire repository.

## Start every session

1. Confirm the active branch and worktree state with `git status --short --branch`.
2. Read `PROJECT_STATUS.md`, `DECISIONS.md`, `DATA_DICTIONARY.md`, and `BACKLOG.md` before changing files.
3. Preserve unrelated user changes. Do not reset, discard, or overwrite them.
4. Work on `dev` unless the user explicitly directs otherwise.

## Source-data safety

- Treat all paths in `config/source_paths.local.json` as immutable, read-only evidence.
- Never write beside, rename, normalize, repair, or delete original source files.
- Never commit original Rose COG databases, DAT files, DLLs, decompiler project files, local path configuration, or private source manifests.
- Generated intermediate data belongs under ignored `var/`; reviewed engine-neutral exports will later receive an explicit tracked location and licensing decision.
- Preserve raw bytes and provenance. Do not replace uncertain source values with inferred values without labeling the inference.

## Reverse-engineering discipline

- Every decoded field must cite its source database/table/row and byte offset or other evidence when the pipeline supports it.
- Use the confidence grades in `docs/CONVENTIONS.md`.
- Unknown data stays unknown and remains preserved. Do not silently discard unfamiliar record types or fields.
- Prefer deterministic scripts and tests over manual edits to generated files.
- Treat synthetic graph coordinates and inferred regions as derived presentation data, not original world facts.

## Completion and handoff

Before ending a material work session:

1. Run relevant tests and record exact commands/results.
2. Update `DATA_DICTIONARY.md` for decoding discoveries.
3. Update `DECISIONS.md` for durable choices.
4. Update `PROJECT_STATUS.md` with changes, evidence, tests, unresolved questions, and the exact next task.
5. Update `BACKLOG.md` to reflect completed and newly discovered work.
6. Commit coherent changes on `dev`; push when authentication and network state permit.
