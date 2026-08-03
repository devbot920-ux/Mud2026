# Three.js comparison prototype

This is the browser candidate for the Phase 5 engine comparison. It consumes the unchanged `mud2026.engine-neutral-world` `1.0.0` Pendelhaven export and renders one authoritative room at a time as a first-person placeholder chamber.

## Setup

Node.js 24 LTS is recommended. Dependencies and their transitive versions are pinned in `package-lock.json`.

```powershell
cd C:\code\Mud2026-web\prototypes\web
& 'C:\Program Files\nodejs\npm.cmd' install
& 'C:\Program Files\nodejs\npm.cmd' run prepare:fixture
& 'C:\Program Files\nodejs\npm.cmd' run dev
```

Open `http://127.0.0.1:4173`. The prepare step verifies SHA-256 `146D19341A7172EFA604E7E32D9277A9E86750ADE26D5637CFDA1EDBBDDE2DA4` before copying the private export. `public/private/`, `dist/`, and `node_modules/` are ignored. Never commit the prepared fixture or a production build containing it.

## Controls and behavior

- Click the chamber to capture the mouse; use mouse look and WASD movement.
- Walk close to an exit arch to follow that exact directed edge.
- Submit `n`, `s`, `e`, `w`, `ne`, `nw`, `se`, `sw`, `u`, `d`, their full names, or `look` in the command bar.
- Press `H` to reveal/suppress hidden exits and backtick to toggle provenance/debug data.
- Colored arches distinguish ordinary exits, door sides, hidden exits, and boundary stubs.
- Multiple arches remain distinct for parallel same-direction edges. In the fixture, room 4057's west edge leads to 4058 and room 4058's west edge remains west; no inverse is invented.
- NPCs and items appear as labeled red and amber markers using the fixture's room-keyed spawn records.

The prototype intentionally does not implement collision physics, door open/lock state, inventory, NPC AI, combat, persistence, or full-world geometry. Command travel chooses the first canonical edge when multiple visible edges share a direction; walking through labeled arches disambiguates them.

## Verification

```powershell
& 'C:\Program Files\nodejs\npm.cmd' test
& 'C:\Program Files\nodejs\npm.cmd' run build
```

Tests use only a small synthetic fixture and cover contract/reference checks, hidden and vertical exits, parallel edges, boundary stubs, spawns, and the unusual 4057/4058 same-west relationship.
