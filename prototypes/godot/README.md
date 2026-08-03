# Godot comparison prototype

This is the Godot 4.7.1 implementation of the Pendelhaven engine spike. It consumes the unchanged private `mud2026.engine-neutral-world` `1.0.0` fixture from outside the project and creates its entire 3D room stage and interface in typed GDScript.

## Run

The private fixture is deliberately neither copied nor committed. Pass its absolute path after `--`:

```powershell
& C:\code\Godot\Godot_v4.7.1-stable_win64_console.exe --path C:\code\Mud2026-godot\prototypes\godot -- --fixture=C:\code\Mud2026\var\exports\pendelhaven-v1.json
```

Alternatively set `MUD2026_FIXTURE_PATH`, or place a local copy at `local/pendelhaven-v1.json`; `local/` is ignored.

Use WASD and the mouse to move, Escape to release/capture the pointer, exit buttons to choose a precise edge, or MUD commands including `n`, `sw`, `u`, `d`, and `look`. Hidden exits are excluded until the developer toggle is enabled. Blue-green arches are internal exits, blue arches cross the fixture boundary, purple arches are hidden, and gold/brown arches are doors.

The room is a reusable stage rather than an invented spatial reconstruction. Each canonical directed edge creates its own portal and UI entry. Edge IDs remain distinct, parallel edges are retained, and the unusual west edge in each direction between rooms 4057 and 4058 is not normalized.

## Test

```powershell
& C:\code\Mud2026-godot\prototypes\godot\run_tests.ps1
```

The headless suite loads the corrected private fixture, enforces its contract and exact family counts, checks room/spawn/entity references, exercises hidden and boundary edges, and asserts the 4057/4058 same-west records remain separate.

## Prototype boundaries

- Placeholder geometry only; room coordinates are not treated as authored 3D layout.
- Doors are visually represented but not yet stateful.
- NPC and item spawns are visual markers, not gameplay actors.
- Walking through a portal or selecting its button transitions to the destination room.
- Description strings remain only in the ignored external fixture and are rendered at runtime.
- A packaged build requires Godot 4.7.1 export templates. Editor/headless execution is sufficient for this comparison spike.
