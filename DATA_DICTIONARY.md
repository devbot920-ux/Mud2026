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

## Derived topology audit baseline

These values are confirmed only with respect to the current derived `graph.json` whose SHA-256 is `C499A15CDDB7548D96914EE1E9571A876E9C388358A30F14FA52617F26202B24`. They are not yet confirmed source semantics.

| Finding | Value | Confidence |
|---|---:|---|
| Unique rooms | 3,446 | Confirmed for derived graph |
| Directed edges | 7,077 | Confirmed for derived graph |
| Weak components | 50 | Confirmed for derived graph |
| Strong components | 79 | Confirmed for derived graph |
| Rooms reachable from seed room 1 | 2,918 | Confirmed for derived graph |
| Edges lacking inverse-direction counterpart | 169 | Confirmed for derived graph |
| Reverse pairs disagreeing on door/hidden state | 17 | Confirmed for derived graph |
| Vertical edges | 104 | Confirmed for derived graph |
| Cross-region edges | 47 | Confirmed for derived graph |
| Same-region coordinate collisions | 184 | Confirmed for derived layout |

The 169 asymmetric edges are structurally classified as 69 reverse endpoints with non-opposite directions, 65 plain one-way links, 14 door links, 14 vertical links, 4 cross-region links, 2 portal/transport-endpoint links, and 1 hidden link. These classifications describe structure only; intent remains unknown.

## Phase 1 canonical baseline

Generated privately at `var/baseline/rose-baseline.sqlite` from the tracked `schema/baseline.sql` and `scripts/baseline_import.py`.

| Entity | Records | Distinct stable IDs | Confidence |
|---|---:|---:|---|
| Source databases | 13 | 13 | Confirmed |
| Source schema objects | 97 | 97 | Confirmed |
| Source rows | 16,720 | — | Confirmed |
| Source values | 58,531 | — | Confirmed |
| DES1 descriptions | 4,398 | 4,397 | Strong ID / tentative text decoding |
| Rooms | 3,446 | 3,446 | Strong ID / tentative fields |
| Doors | 78 | 78 | Strong ID / tentative topology |
| Item-base records | 549 | 529 | Strong ID / tentative categories |
| NPCs | 211 | 211 | Strong ID / tentative descriptions |
| Spawn records | 387 | 387 | Strong ID / tentative entries |
| Source-decoded topology edges | 7,097 | 7,097 semantic tuples | Tentative decoding |
| MOD1 tag values cataloged | 113 | 113 | Confirmed at assumed offset 8 |

The baseline reproduces every published graph node and edge while retaining 20 additional source-decoded edges. Nineteen collide with another edge from the same room/direction in the legacy builder; one shares endpoints with another direction and was collapsed by a simple directed graph representation.

Canonical raw tables are `source_file`, `schema_object`, `source_row`, and `source_value`. Additive interpretation tables are `decoded_entity`, `decoded_field`, `topology_edge`, and `mod1_tag_catalog`. `import_run` records the schema version and semantic digest.

## Canonical topology audit

The canonical Phase 2 audit uses all 7,097 source-decoded edges. It uses `graph.json` only to attach derived region, coordinate, portal/transport, and other presentation attributes.

| Finding | Canonical value | Change from derived graph | Confidence |
|---|---:|---:|---|
| Rooms | 3,446 | 0 | Strong identity |
| Directed edges | 7,097 | +20 | Tentative decoding with source provenance |
| Weak components | 49 | -1 | Strong for canonical edge set |
| Strong components | 63 | -16 | Strong for canonical edge set |
| Rooms reachable from seed room 1 | 3,383 | +465 | Strong for canonical edge set |
| Rooms unreachable from seed room 1 | 63 | -465 | Strong for canonical edge set |
| Missing inverse-direction counterparts | 189 | +20 | Strong structural finding |
| Door/hidden inconsistent reverse pairs | 17 | 0 | Strong structural finding |
| Vertical edges | 104 | 0 | Tentative direction decoding |
| Cross-region edges | 49 | +2 | Tentative topology plus derived regions |

Canonical asymmetric edges are structurally grouped as 106 reverse endpoints with non-opposite directions, 60 plain one-way links, 14 vertical links, 4 cross-region links, 2 door links, 2 portal/transport-endpoint links, and 1 hidden link. Intent remains unknown.

Recovered links between rooms 3045 and 3046 connect the formerly separate 322-room component to the main world. Other recovered door directions account for most of the improved directed reachability and strong connectivity.
