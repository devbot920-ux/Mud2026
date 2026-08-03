# Mud2026 Unity comparison prototype

Minimal Unity 6 C# client for the unchanged private Pendelhaven `mud2026.engine-neutral-world` `1.0.0` export. It uses code-generated placeholder geometry so the comparison measures engine workflow rather than asset quality.

## Run

Open this directory in Unity 6. The prototype discovers `C:\code\Mud2026\var\exports\pendelhaven-v1.json`, or set `MUD2026_FIXTURE` to another unchanged private export. The fixture is never copied or committed.

- WASD and mouse: first-person movement
- Walk into cyan/brown exit markers: travel using the selected canonical edge
- Commands: `n s e w ne nw se sw u d look`
- `Show hidden exits`: reveal magenta hidden markers
- The overlay exposes room, edge, confidence/provenance-presence, parallel-edge IDs, and stub destinations

NPCs are red placeholders and items are yellow placeholders. Brown exits are doors. Vertical exits are positioned above/below the room center.

## Verification

```powershell
$unity = 'C:\Program Files\Unity\Hub\Editor\6000.5.6f1\Editor\Unity.exe'
& $unity -batchmode -nographics -projectPath C:\code\Mud2026-unity\prototypes\unity -runTests -testPlatform EditMode -testResults C:\code\Mud2026-unity\prototypes\unity\TestResults.xml -logFile C:\code\Mud2026-unity\prototypes\unity\Logs\editmode.log
& $unity -batchmode -nographics -projectPath C:\code\Mud2026-unity\prototypes\unity -executeMethod Mud2026.UnityPrototype.Editor.BuildPrototype.BuildWindows -logFile C:\code\Mud2026-unity\prototypes\unity\Logs\build.log -quit
```

The tests include an embedded synthetic, non-proprietary multiedge fixture plus an external acceptance check that never copies private content. At runtime the loader additionally enforces exact private fixture counts (63/130/2/18/12/19/70), unique IDs, referential integrity, valid directions, hidden/vertical exits, boundary room references, and the unusual `4057 W -> 4058` plus `4058 W -> 4057` pair.

## Deliberate limitations

- This is an engine-comparison spike: no combat, inventory, persistence, production art, networking, or authored scenes.
- When multiple canonical edges share a command direction, text travel reports the multiplicity and deterministically chooses the first edge; walking portals expose each edge independently.
- The runtime uses the classic Unity input axes to avoid an extra input-asset dependency.
