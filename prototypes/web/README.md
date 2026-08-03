# Three.js comparison prototype

This is the browser candidate for the Phase 5 engine comparison. It consumes the unchanged `mud2026.engine-neutral-world` `1.0.0` Pendelhaven export and renders one authoritative room at a time as a first-person chamber. Room 3976 also demonstrates original generated GLB models for a data-driven room, NPC, and item.

## Setup

Node.js 24 LTS is recommended. Dependencies and their transitive versions are pinned in `package-lock.json`.

```powershell
cd C:\code\Mud2026\prototypes\web
& 'C:\Program Files\nodejs\npm.cmd' install
& 'C:\Program Files\nodejs\npm.cmd' run prepare:fixture
& 'C:\Program Files\nodejs\npm.cmd' run dev
```

Open `http://127.0.0.1:4173`. The prepare step verifies SHA-256 `146D19341A7172EFA604E7E32D9277A9E86750ADE26D5637CFDA1EDBBDDE2DA4` before copying the private export. `public/private/`, `dist/`, and `node_modules/` are ignored. Never commit the prepared fixture or a production build containing it.

## Controls and behavior

- Click the chamber to capture the mouse; use mouse look and WASD movement. Room 3976 constrains movement at its modeled walls.
- Face the nearby old man or parchment and press `E` when the interaction prompt appears.
- Walk close to an exit arch to follow that exact directed edge.
- Submit `look`, `examine old man`, `talk to old man`, `read parchment`, or `take parchment` to play room 3976 entirely through MUD-style commands.
- Submit `n`, `s`, `e`, `w`, `ne`, `nw`, `se`, `sw`, `u`, `d`, or their full names to travel.
- Submit `diagnose` in room 3976 for an in-game check of model loading, collision, targeting, commands, and the authoritative west exit.
- Press `H` to reveal/suppress hidden exits and backtick to toggle provenance/debug data.
- Colored arches distinguish ordinary exits, door sides, hidden exits, and boundary stubs.
- Multiple arches remain distinct for parallel same-direction edges. In the fixture, room 4057's west edge leads to 4058 and room 4058's west edge remains west; no inverse is invented.
- NPCs and items appear as labeled red and amber markers using the fixture's room-keyed spawn records.
- Room 3976 replaces its generic chamber with a generated stone training room. NPC 3993 and item 3985 load generated low-poly models, while the old man's circular ground marker remains for readability.

## Initial room models

The committed GLB assets in `public/models/generated/` are original procedural models generated with Blender 5.2. Regenerate all three plus a local preview with:

```powershell
cd C:\code\Mud2026
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python prototypes\web\tools\generate_initial_room_models.py
```

The generator writes its preview to ignored `var/previews/initial-room-models.png`. Model loading is generation-guarded so a slow request cannot insert assets from a room the player has already left.

Room 3976 is a functional tutorial-room vertical slice with collision boundaries, proximity/facing interaction, canonical descriptions, tutorial progress, text-command equivalents, and westward travel. Other rooms remain comparison-prototype chambers. Door open/lock state, inventory, NPC AI, combat, persistence, and full-world geometry are not yet implemented. Command travel chooses the first canonical edge when multiple visible edges share a direction; walking through labeled arches disambiguates them.

## Verification

```powershell
& 'C:\Program Files\nodejs\npm.cmd' test
& 'C:\Program Files\nodejs\npm.cmd' run build
```

Tests use only synthetic/public rule inputs. They cover contract/reference checks, hidden and vertical exits, parallel edges, boundary stubs, spawns, the unusual 4057/4058 same-west relationship, room 3976 wall constraints, interaction targeting, and tutorial command parsing.
