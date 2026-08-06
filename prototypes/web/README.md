# Three.js comparison prototype

This is the browser candidate for the Phase 5 engine comparison. It consumes the unchanged `mud2026.engine-neutral-world` `1.0.0` Pendelhaven export and renders one authoritative room at a time as a first-person chamber. Rooms 3976 through 3984 form a modeled tutorial route, and rooms 4165 through 4173 form the modeled central Pendelhaven hub.

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

- Create one of the six source-documented races (Human, Elf, Dwarf, Gnome, Giant, or Fairfolk) and choose one of the six starting walks of life (Warrior, Scholar, Gypsy, Priest, Mage, or Archtypical).
- Press `I` for the graphical pack/equipment menu and `C` for the character sheet. The sheet shows all eight Rose attributes, derived combat/resources, encumbrance, and six core proficiencies with their prime-attribute adjustment.
- Press `Enter` to leave mouse-look and focus the MUD command line. Use the visible **Commands** / **Return to mouse** button to switch modes, or click the 3D world to resume mouse-look.
- Third-person is the default. Click the chamber to capture the mouse, use mouse look and WASD movement, tap `V` to toggle first-person, or hold `V` and use the mouse wheel to adjust third-person distance.
- Hold `Shift` while moving to sprint. Sprinting animates the avatar, increases speed, and drains movement points; walking or resting restores them.
- Aim the reticle at any spawned NPC or item to display its extracted description automatically. Approach and press `E` when an action prompt appears.
- Walk close to an exit arch or vertical passage to follow that exact directed edge. After travel, the player appears just inside the arrival side and faces into the room.
- Submit `look`, `examine old man`, `talk to old man`, `read parchment`, or `take parchment` to play room 3976 entirely through MUD-style commands.
- Submit `n`, `s`, `e`, `w`, `ne`, `nw`, `se`, `sw`, `u`, `d`, or their full names to travel.
- Submit `diagnose` in room 3976 for an in-game check of model loading, collision, targeting, commands, and the authoritative west exit.
- Press `H` to reveal/suppress hidden exits and backtick to toggle provenance/debug data.
- Colored arches distinguish ordinary exits, door sides, hidden exits, and boundary stubs.
- Multiple arches remain distinct for parallel same-direction edges. In the fixture, room 4057's west edge leads to 4058 and room 4058's west edge remains west; no inverse is invented.
- NPCs and items appear as labeled red and amber markers using the fixture's room-keyed spawn records.
- Room 3976 replaces its generic chamber with a generated stone training room. NPC 3993 and item 3985 load generated low-poly models, while the old man's circular ground marker remains for readability.
- Each room from 3977 through 3984 has a distinct generated shell matching its extracted purpose. Only canonical graph exits receive openings and travel triggers.
- Ambient motion is room-specific: start-room torch flicker, council recitation pulses, library dust, discarded-paper movement, wardroom knife glints, market-sign sway, a pulsing practice ring with combat-responsive dummy motion, glowing dais symbols, and an altar light.
- Every canonical NPC/mob on the route (3993–3998) has a full-body description-driven GLB: the old official, three distinct language instructors, the lazy halberd guard, and the rag-draped wooden dummy. Their idle motion matches their role while circular ground rings preserve gameplay readability.
- The nearby training route is playable: `W, W, NW, N` reaches room 3980, where `GET KNIFE` (or `E`) adds a knife to inventory. `NE, E` then reaches room 3982, where `ATTACK DUMMY`, `A DUMMY`, or `E` begins timed practice combat. Continue `E, U` across the symbol-covered dais to reach room 3984's advancement altar. `STOP` disengages and `INVENTORY`/`I` opens the pack.
- Continue `SE` into Pendelhaven Square. All nine central rooms have description-driven environments and all eight named inhabitants have individual models.
- In Pendelhaven Arena (4168), press `E` at the gong or type `RING GONG` to summon one of four extracted opponents. Aim and press `E`, or type `ATTACK SLUG`, `ATTACK KOBOLD`, `ATTACK KOBOLD THUG`, or `ATTACK KOBOLD GUARD`.
- Arena opponents fight back. Maximum health depends on race, class, and level; defeat respawns the player at full health in Pendelhaven Hospice while preserving progression and equipment. The arena cycles through giant slug, kobold, kobold thug, and hammer-bearing kobold guard models.
- Canonical hostile spawns in the cellar and excavated tunnels also fight back. Victories award experience and deterministic equipment drops; defeated world mobs return after roughly 30 seconds.
- Use `INVENTORY`, `STATS`, `SKILLS`, `ARM <item name>`, `EQUIP <item name>`, `DISARM`, and `UNEQUIP [weapon|armor]` as command-mode equivalents. Weapons increase damage, armor reduces incoming damage, and equipped weapons appear on the third-person avatar.
- Rendering uses ACES tone mapping, soft 2048px shadows, bloom, higher-detail lighting, damage flashes/numbers, and original generated stone and oak textures.

## Initial room models

The committed GLB assets in `public/models/generated/` are original procedural models generated with Blender 5.2. Regenerate the start-room assets and the eight remaining route rooms with:

```powershell
cd C:\code\Mud2026
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python prototypes\web\tools\generate_initial_room_models.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python prototypes\web\tools\generate_training_route_models.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python prototypes\web\tools\generate_training_characters.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python prototypes\web\tools\generate_pendelhaven_hub_models.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python prototypes\web\tools\generate_pendelhaven_characters.py
```

The generators write ignored previews under `var/previews/`. Model loading is generation-guarded so a slow request cannot insert assets from a room the player has already left.

Room 3976 is a functional tutorial-room vertical slice with collision boundaries, gaze/proximity interaction, canonical descriptions, tutorial progress, text-command equivalents, and westward travel. The exported rooms through 3984 add inventory, practice-dummy combat, and working vertical traversal. The central hub adds modeled shops and civic spaces, solid major furnishings, third-person character rendering, reciprocal combat, health/movement/mana, source-aligned race and walk-of-life choices, attributes, proficiencies, experience/levels, weighted equipment, victories, and hospice respawning. Exact original numerical formulas are still being decoded, so current balancing math is explicitly prototype-defined; see `docs/GAMEPLAY_RULES.md`. Door open/lock state, persistence, a full economy, spellcasting, quests, and full-world geometry are not yet implemented.

## Verification

```powershell
& 'C:\Program Files\nodejs\npm.cmd' test
& 'C:\Program Files\nodejs\npm.cmd' run build
```

Tests use only synthetic/public rule inputs. They cover contract/reference checks, navigation, targeting, commands, combat, all eight attributes, source-aligned race/walk differences, derived resources, proficiencies, progression, inventory weight, equipment-slot replacement, and camera controls.
