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

## Prototype rules currently implemented

`prototypes/web/src/rpg.ts` provides deterministic, tested working values:

- Race and walk modifiers start from 35 in each attribute, within the original help system's stated average band of roughly 21–50.
- Constitution and level derive health; constitution and dexterity derive movement points; intelligence, constitution, and level derive mana.
- Strength derives unarmed damage and combines with constitution for carrying capacity.
- Dexterity and constitution reduce the player's attack interval.
- Equipment has a prototype weight plus either weapon damage or armor absorption. Only one weapon and one armor item can be equipped at a time.
- Six core proficiencies have walk-specific raw starting values and a visible prime-attribute adjustment.
- Sprint drains movement points; walking/resting restores them. Gnomes regenerate mana twice as fast, matching the recovered racial description.

These numeric modifiers, formulas, starter proficiency values, loot weights, and loot bonuses are presentation/gameplay decisions, not decoded original constants. The Character menu says this in-game.

## Current UI and commands

- `I` or `INVENTORY` opens the pack, weight/capacity summary, equipment slots, and Equip/Unequip buttons.
- `C`, `ST`, `STATS`, `ATTRIBUTES`, `SKILLS`, or `SHOWPROFS` opens the character sheet.
- `ARM <item>` and `EQUIP <item>` equip owned gear. `DISARM`, `UNEQUIP`, and `REMOVE` clear a slot.
- `Enter` changes from mouse-look to command entry. The control-mode button or clicking the world returns to mouse-look.

## Evidence

- `C:\dos\modules\RCI_HEL1.db`, `data_t`: topics 36–38, 42–74, 81–86, and 119–124. Aliases are exposed through converted keys; long help text is decoded as CP437 provisionally.
- `C:\temp\decompileproject\decomp2\RCIROSE.DLL.c`: `_GET_MAXENCUMBERANCE`, `_GET_CURENCUMBERANCE`, `_INVENTORY`, `_PCWEAR`, `_CAN_WEAR`, `_CAN_WEAR2`, `_IS_EQUIPPED_AT`, and `_LOCATE_EQUIPPED`.
- `scripts/baseline_import.py`: the eight-attribute and known-skill identifier maps used by the provenance baseline.

Exact original formulas and record layouts remain research tasks. Source files were inspected read-only.
