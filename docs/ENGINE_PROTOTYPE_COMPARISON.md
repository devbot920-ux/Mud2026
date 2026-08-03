# Phase 5 Engine Prototype Comparison

All three prototypes consume the same private `mud2026.engine-neutral-world` `1.0.0` Pendelhaven export. The source export is not committed. The corrected comparison fixture has SHA-256 `146D19341A7172EFA604E7E32D9277A9E86750ADE26D5637CFDA1EDBBDDE2DA4`.

## Shared behavior

Each client validates the contract, expected family counts, edge/entity references, unique edge IDs, boundary stubs, hidden and vertical exits, parallel multiedges, and the unusual pair `4057 W -> 4058` plus `4058 W -> 4057`. Each renders a presentation-derived room stage with first-person movement, directed exit portals, text commands, room text, NPC/item placeholders, and developer information. None interprets unresolved modifiers.

## Results

| Candidate | Toolchain | Automated evidence | Build/run evidence | Main tradeoff |
|---|---|---|---|---|
| Godot | Godot 4.7.1 Standard, typed GDScript | 15 synthetic/private assertions; editor import and headless runtime passed | Runs in editor/headless; packaged export pending matching templates | Best balance of complete engine features, readable code, licensing, and solo maintenance |
| Unity | Unity 6000.5.6f1, C#, Newtonsoft JSON | 5/5 EditMode tests including private fixture acceptance | Windows x64 development build succeeded, approximately 148.5 MB | Strong tooling and mature pipeline, but largest project/build and more generated settings |
| Three.js | Node 24, TypeScript, Three.js, Vite | 10/10 tests; zero npm audit findings | Browser smoke passed; JS 492.15 kB / 124.98 kB gzip | Fastest URL-first workflow, but collision, navigation, and game architecture remain project-owned |

The browser smoke loaded the real private fixture, rendered room `3976`, and followed command `w` to room `3977` without console errors. Unity produced a runnable Windows development build. Godot ran the real fixture successfully through the editor/headless runtime, but matching export templates were not installed.

## Prototype locations

- `prototypes/godot` — run and test commands in its README
- `prototypes/unity` — editor, EditMode test, and Windows build commands in its README
- `prototypes/web` — fixture preparation, development server, tests, and build commands in its README

Generated builds, engine caches, dependency trees, and the private fixture are ignored.

## Evaluation conclusion

Godot remains the technical recommendation for the first sustained playable client. It keeps the authoritative graph/data model simple while providing collision, navigation, UI, asset import, Windows/web export, and a compact code-first project. Three.js is the strongest rapid browser option and should remain a useful contract/interaction reference. Unity is fully viable but adds the most project and build overhead for this solo private game.

The selection remains provisional until the owner performs the same short hands-on route in all three clients and evaluates movement feel, editor workflow, iteration speed, and preferred deployment target.

## Hands-on comparison route

1. Start each client with the corrected private fixture.
2. Confirm room `3976` appears with description and visible exits.
3. Travel west to `3977` using both movement and the command bar.
4. Toggle hidden exits and use one vertical exit.
5. Inspect an NPC/item placeholder and the developer overlay.
6. Visit rooms `4057` and `4058` and confirm both directed records remain west.
7. Record startup time, iteration friction, movement/UI preference, and whether native or browser deployment feels more useful.

Combat, inventory, persistence, production assets, networking, stateful doors, and guessed unknown-modifier behavior were intentionally excluded.
