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

## HEL1 gameplay/help evidence

Read-only inspection of converted `RCI_HEL1.db` confirms 189 keyed help records. `keys_t` identifies a two-byte numeric topic key at offset 0 and five 30-byte text-key segments at offsets 2, 32, 62, 92, and 122. The converted `data_t.key_1` through `key_5` values expose command aliases including `inventory`/`inv`/`I`, `equip`/`arm`, `stats`/`attributes`, and `skills`/`showprofs` (Strong for keys and aliases).

CP437/NUL-segment reading of the longer record bodies is still provisional, but consistently documents six races, six starting walks of life, eight attributes, prime-requisite proficiency adjustment, mana, health, attack/action delays, armor class versus absorption, equipped slots, and encumbrance measured in troys (Tentative text decoding; Strong semantic corroboration where matching DLL consumers exist). A concise implementation/evidence ledger is tracked in `docs/GAMEPLAY_RULES.md`.

## Currently interpreted MOD1 tags

These meanings come from the existing research scripts and must be revalidated during Phase 1/3.

| Tag | Working meaning | Confidence |
|---|---|---|
| `0x0A` | Base room | Strong |
| `0x0D` | Door/door connection | Strong |
| `0x28` | NPC base | Strong |
| `0x30` | Room spawn modifier | Strong |
| `0x32` | Item base | Strong |
| `0x33` | Weapon modifier/category | Strong |
| `0x34` | Armor modifier/category | Strong |
| `0x37` | Store/shop | Strong |
| `0x48` | Skill trainer | Tentative |
| `0x6D` | Peaceful/no-attack room | Tentative |
| `0x6E` | Spell trainer/list | Tentative |
| `0x72` | Tavern | Tentative |
| `0x75` | Promotion room | Tentative |
| `0x85` | Attribute trainer | Tentative |
| `0xA6`–`0xAF` | Hidden exits by direction | Strong |
| `0xC5` | Quest room/text | Tentative |
| `0xCC` | Potion modifier/category | Strong |
| `0xE0` | Trap modifier | Tentative |

## Phase 3 MOD1 hypotheses

These meanings are supported by decompiled `_ACQUIRE_MODIFICATION` consumers and data associations. They classify tags; they do not yet define complete byte layouts.

| Tag or range | Working meaning | Confidence | DLL evidence |
|---|---|---|---|
| `0x5D` | Door strength or key rule | Tentative | `PICKSTRENGTH`, `DOORSTRENGTH`, `STEALSKEY` |
| `0x76`–`0x7D` | NPC extra-attack slots 1–8 | Strong | `NPC_PRE_ATTACK`, `GET_XTRA_ATTACK` |
| `0x8A`–`0x93` | Disease effect slots 1–10 | Tentative | disease tests, cure, and death cleanup |
| `0x94`–`0x9D` | Poison effect slots 1–10 | Tentative | poison tests, antidote/cure, and death cleanup |
| `0xB2` | Armor defense eligibility | Strong | `GET_AC`, `GET_AC2`, `GET_DPOOL` |
| `0xE1`–`0xE3` | Trap event components | Strong | `DO_TRAP_EVENTS` |
| `0xE4` | Limited shop stock | Strong | `LIMITED_AVAILABLE`, `PC_BUYITEM`, shop stock |
| `0xEE`–`0xF0` | Conditional combat modifiers | Strong | bane to-hit/AC/defense-pool and damage multiplier |

Only tag values present in the snapshot appear in the generated catalog; absent members of a DLL-observed range remain hypotheses rather than invented records. The detailed ignored report records evidence and confidence for all 118 present tags, including 77 with no assigned semantic name.

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
| Item-base records | 529 | 529 | Strong ID / tentative categories |
| NPCs | 211 | 211 | Strong ID / tentative descriptions |
| Spawn records | 333 | 333 | Strong ID / tentative entries |
| Source-decoded topology edges | 7,097 | 7,097 semantic tuples | Tentative decoding |
| MOD1 tag values cataloged | 118 | 118 | Confirmed little-endian `u16` at offsets 8–9 |

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

## Phase 4 engine-neutral fixture

The ignored `var/exports/pendelhaven-v1.json` implements contract `mud2026.engine-neutral-world` version `1.0.0`.

| Export concept | Records | Interpretation |
|---|---:|---|
| Primary rooms | 60 | Complete canonical rooms selected by derived `R02` membership |
| Room stubs | 3 | Minimal external endpoints `416`, `958`, `4061` |
| Directed edges | 130 | 125 internal plus 5 boundary; canonical multiedges |
| Door sides | 2 | Separate `4057` and `4058` source records; both decode direction `W` |
| Spawns / entries | 19 / 32 | All selected-room spawn records and decoded entries |
| Referenced NPCs | 18 | Complete typed spawn closure |
| Referenced items | 12 | Complete typed spawn closure |
| Associated modifiers | 70 | Every non-base same-key MOD1 row for primary rooms and referenced entities |

Of the 70 modifiers, 21 use a current interpreted/hypothesized tag and 49 retain unknown meaning. All retain complete private raw bytes and provenance. Decoded fields retain per-field confidence; tag-level Phase 3 hypotheses are not promoted to confirmed fields.

## RCI_SPEL fixed-width records

`RCI_SPEL.db` contains 97 fixed-width 405-byte spell records. `scripts/export_spell_fixture.py` opens the database immutable/read-only and writes the ignored `var/exports/spells-v1.json` contract. The following offsets are corroborated by casting consumers in `RCIROSE.DLL.c`:

| Offset | Width | Meaning | Confidence |
|---:|---:|---|---|
| 0 | 80 | spell name, NUL-terminated | Confirmed |
| 80 | 10 | command abbreviation | Confirmed |
| 90 | 2 | spell ID, little-endian | Confirmed |
| 332–333 | 1 each | primary / secondary sphere | Strong |
| 336–337 | 1 each | primary / secondary proficiency requirement | Strong |
| 338 | 1 | mana cost | Confirmed |
| 339 | 1 | effect dispatch type | Strong |
| 340 | 2 | base recovery delay | Strong |
| 349+ | triplets spaced 8 bytes | effect numeric arguments | Strong per handler |
| 389–397 | five signed 16-bit values | effect-handler indexes, `-1` sentinel | Strong |
| 399–403 | 1 each | target flags | Tentative semantics |
| 404 | 1 | damage type | Strong |

Handler 0 (`_CAUSE_DAMAGE`) rolls the first triplet as `dice_count` independent inclusive rolls from `roll_min` through `roll_max`. Handler 1 (`_HEALING_HITPOINTS`) rolls caster-level dice whose inclusive bounds are the triplet's first and second values. `_CAST_EFFECTTYPE1` succeeds when d100 is no greater than `85 + casting bonus + proficiency delta`; `_CAST_SPELL` consumes the record's mana cost.

`_SPELL_RDELAY` is confirmed to return no more than the record's base delay, but a helper in the decompile remains opaque. Client recovery reduction is therefore an isolated prototype approximation. Walk-number-to-name mapping, starter spell ownership, and initial sphere proficiency values also remain tentative/prototype rules.

## Combat formula evidence

`_GET_TOHIT` confirms a d100-shaped check involving adjusted weapon proficiency, weapon proficiency requirement, target armor class, attack bonuses, and a one-third over-encumbrance penalty. `_ATTACK_PVNPC` derives damage dice from opposing offense and defense pools, then calls the same inclusive `_ROLLDICE` helper with weapon-record bounds. Exact item damage-bound and requirement fields are not yet decoded, so the web client implements this confirmed structure with explicitly prototype-only equipment ranges and requirements.
