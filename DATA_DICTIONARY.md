# Data Dictionary

This is a living catalog. A listed meaning is not necessarily confirmed; consult its confidence and evidence.

## Confidence grades

- **Confirmed** — demonstrated by authoritative code behavior or multiple independent tests.
- **Strong** — supported by consistent data structure plus corroborating evidence.
- **Tentative** — plausible working interpretation with incomplete corroboration.
- **Unknown** — preserved but not interpreted.

Detailed rules appear in `docs/CONVENTIONS.md`.

## Source databases

| Database | Rows | Current interpretation | Confidence |
|---|---:|---|---|
| RCI_MOD1 | 7,060 | Module/world records | Strong |
| RCI_DES1 | 4,398 | Long descriptions keyed by embedded identifier | Strong |
| RCI_INS1 | 4,185 | Undecoded record family | Unknown |
| RCI_NAM1 | 673 | Names or indexed text | Tentative |
| RCI_HEL1 | 189 | Help/command text | Tentative |
| RCI_SPEL | 97 | Spell definitions | Strong |
| RCI_ACT1 | 64 | Actions or commands | Tentative |
| RCI_RAND | 17 | Random definitions/tables | Tentative |
| RCI_CLAN, RCI_INS2, RCI_MOD2, RCI_PLAY, RCI_UNIV | 0 | Empty snapshot/template databases | Strong for row count; semantics unknown |

## Currently interpreted MOD1 tags

These meanings come from the existing research scripts and must be revalidated during Phase 1/3.

| Tag | Working meaning | Confidence |
|---|---|---|
| `0x0A` | Base room | Strong |
| `0x0D` | Door/door connection | Strong |
| `0x28` | NPC base | Strong |
| `0x30` | Room spawn modifier | Strong |
| `0x32` | Item base | Strong |
| `0x33` | Weapon modifier/category | Tentative |
| `0x34` | Armor modifier/category | Tentative |
| `0x37` | Store/shop | Strong |
| `0x48` | Skill trainer | Tentative |
| `0x6D` | Peaceful/no-attack room | Tentative |
| `0x6E` | Spell trainer/list | Tentative |
| `0x72` | Tavern | Tentative |
| `0x75` | Promotion room | Tentative |
| `0x85` | Attribute trainer | Tentative |
| `0xA6`–`0xAF` | Hidden exits by direction | Tentative |
| `0xC5` | Quest room/text | Tentative |
| `0xCC` | Potion modifier/category | Tentative |
| `0xE0` | Trap modifier | Tentative |

## Existing derived graph

`C:\temp\DoorTelnet\graph.json` is noncanonical derived output. It contains room nodes, directional edges, display coordinates, region membership/names, descriptions, selected room flags, and spawn references.

The X/Y layout and at least some region assignments were produced by scripts. They must be represented as derived values, not source-authored coordinates.
