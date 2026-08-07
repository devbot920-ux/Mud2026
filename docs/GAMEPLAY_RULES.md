# Gameplay rules ledger

This ledger separates recovered Rose COG concepts from balancing rules invented for the playable web prototype. It does not claim that prototype numbers reproduce the original server.

## Recovered gameplay concepts

The converted `RCI_HEL1.db` help table documents six starting races: Human, Elf, Dwarf, Gnome, Giant, and Fairfolk. It documents six starting “walks of life”: Warrior, Scholar, Gypsy, Priest, Mage, and Archtypical/Commoner. A walk affects how efficiently a character learns proficiencies rather than permanently excluding other skills. Level-30 specializations are described but are not yet implemented.

The same source documents eight attributes: strength, wisdom, dexterity, constitution, intelligence, charisma, comeliness, and perception. Its gameplay descriptions associate:

- strength with carried weight, physical damage, and weapon access;
- dexterity with dodging, martial attacks, thieving, and—together with constitution—attack/action speed;
- constitution with maximum hit points, healing, armor access, and attack/action speed;
- wisdom and intelligence with magical proficiencies, with intelligence and constitution contributing to mana capacity;
- perception with archery and thieving;
- charisma with purchase prices, while comeliness describes physical appearance/social advantage.

Proficiencies have a raw value and an adjusted value affected by a prime attribute. Core recovered skill names include Melee Weaponry, Empty Hand Combat, Bowman, Armor Usage, Defensive Dodge, and Magical Defense. The help system distinguishes armor-class avoidance from damage absorption.

Inventory has item weight measured in troys and a maximum encumbrance. Source help describes attack, defense, and movement penalties when encumbered. Weapons must be armed, may require proficiency, and have attack/action delays. Armor occupies defined wear locations and can have walk/proficiency restrictions. Decompiled consumers corroborate inventory lists, equipped slots, weight calculation, wear checks, and maximum/current encumbrance.

The fixed-width spell table and DLL casting consumers now establish exact mana cost, primary/secondary sphere requirements, a d100 success threshold of `85 + casting bonus + proficiency delta`, inclusive damage dice, level-scaled healing dice, and record base recovery delay. The melee consumers establish a d100-shaped proficiency-versus-requirement check affected by armor and one-third of excess encumbrance, followed by inclusive weapon damage rolls.

Promotion is explicit rather than automatic. Recovered help says experience is traded for advancement and attribute points are awarded on promotion. `_PROMOTE` grants `50 + current-level d10 rolls` development points and 2 attribute points; the fixture identifies Pendlehaven Guild as a promotion room capped at level 5. Training help confirms trainer locations, development-point and silver costs, rising costs at higher skill, walk-specific efficiency, and the exact example of 3 development points for a Warrior's starting Melee Weaponry increase.

## Prototype rules currently implemented

`prototypes/web/src/rpg.ts` provides deterministic, tested working values:

- Race and walk modifiers start from 35 in each attribute, within the original help system's stated average band of roughly 21–50.
- Constitution and level derive health; constitution and dexterity derive movement points; intelligence, constitution, and level derive mana.
- Strength derives unarmed damage and combines with constitution for carrying capacity.
- Dexterity and constitution reduce the player's attack interval.
- Equipment has prototype weight, proficiency requirement, damage range, or armor absorption values. Only one weapon and one armor item can be equipped at a time; the attack flow follows the recovered d100/ranged-damage structure.
- Six core proficiencies have walk-specific raw starting values and a visible prime-attribute adjustment.
- Sprint drains movement points; walking/resting restores them. Gnomes regenerate mana twice as fast, matching the recovered racial description.
- Starter spell ownership, initial sphere proficiency, and the bounded recovery reduction are prototype rules. Spell record costs, casting threshold shape, failure, damage rolls, and healing rolls are recovered behavior.
- Strength now directly determines the physical-damage base; trained prime attributes also change adjusted proficiency and therefore melee accuracy.
- The equipment sheet exposes the 12 decoded wearable locations plus the separately armed weapon: torso, arms, legs, feet, head, shield, cloak, two ring locations, necklace, bracers, and amulet.
- `REST` enters the recovered resting state and restores health, movement, and mana while stationary and out of combat. Its tick rates remain prototype balancing.

These numeric modifiers, formulas, starter proficiency values, loot weights, and loot bonuses are presentation/gameplay decisions, not decoded original constants. The Character menu says this in-game.

## Current UI and commands

- `I` or `INVENTORY` opens the pack, weight/capacity summary, equipment slots, and Equip/Unequip buttons.
- `C`, `ST`, `STATS`, `ATTRIBUTES`, `SKILLS`, or `SHOWPROFS` opens the character sheet.
- `K`, `SPELLS`, or `SPELLBOOK` opens the spellbook. `CAST <name or abbreviation>` invokes a known spell.
- `PROMOTE` works only in a source-marked promotion room and only with enough banked experience. `INQUIRE` opens Oscar's training menu when nearby; `TRAIN <skill>` spends development points and `ENHANCE <attribute>` spends attribute points.
- `REST` or `SLEEP` begins recovery. Movement, combat, casting, travel, `WAKE`, or `STAND` ends it.
- `ARM <item>` and `EQUIP <item>` equip owned gear. `DISARM`, `UNEQUIP`, and `REMOVE` clear a slot.
- `Enter` changes from mouse-look to command entry. The control-mode button or clicking the world returns to mouse-look.
- Proximity buttons expose nearby inspection, combat, spell, and exit actions. Engaged mobs chase, can block close exits, and may follow across ordinary fixture edges; sprint across an exit or use `FLEE <direction>` to break through.

## Evidence

- `C:\dos\modules\RCI_HEL1.db`, `data_t`: topics 36–38, 42–74, 81–86, and 119–124. Aliases are exposed through converted keys; long help text is decoded as CP437 provisionally.
- `C:\temp\decompileproject\decomp2\RCIROSE.DLL.c`: inventory consumers plus `_PROMOTE`, `_RESTME`, `_BREAK_REST`, `_IS_EQUIPPED_AT`, `_PCWEAR`, casting consumers, and combat consumers.
- `C:\dos\modules\RCI_SPEL.db`, `data_t`: 97 immutable/read-only 405-byte spell records exported privately by `scripts/export_spell_fixture.py`.
- `scripts/baseline_import.py`: the eight-attribute and known-skill identifier maps used by the provenance baseline.

Exact item fields, some casting target flags/handlers, and the opaque recovery-delay helper remain research tasks. Source files were inspected read-only.
