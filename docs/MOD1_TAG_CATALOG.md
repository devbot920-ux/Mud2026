# MOD1 Tag Evidence Catalog

Phase 3 catalogs every MOD1 tag and ranks unresolved work. It does not claim that every tag or field is decoded. The ignored JSON report retains per-tag provenance, byte variability, co-occurrence, and DLL call-site line numbers.

## Coverage

- 7,060 records across 118 tag values
- 41 interpreted or hypothesized tags; 77 explicitly unresolved
- Source descriptions are excluded from both reports

## Phase 3 promotions

| Tag | Meaning | Confidence | Evidence |
|---|---|---|---|
| `0x005D` | `door_strength_or_key_rule` | tentative | PICKSTRENGTH, DOORSTRENGTH, and STEALSKEY consumers |
| `0x0076` | `npc_extra_attack_slot_1` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x0077` | `npc_extra_attack_slot_2` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x0078` | `npc_extra_attack_slot_3` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x007A` | `npc_extra_attack_slot_5` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x007B` | `npc_extra_attack_slot_6` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x007C` | `npc_extra_attack_slot_7` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x007D` | `npc_extra_attack_slot_8` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x00B2` | `armor_defense_eligibility` | strong | GET_AC, GET_AC2, and GET_DPOOL consumers |
| `0x00E1` | `trap_event_component_1` | strong | DO_TRAP_EVENTS consumer |
| `0x00E4` | `limited_shop_stock` | strong | LIMITED_AVAILABLE, PC_BUYITEM, and shop-stock consumers |
| `0x00EE` | `conditional_combat_modifier_1` | strong | bane to-hit, AC, defense-pool, damage multiplier consumers |
| `0x00EF` | `conditional_combat_modifier_2` | strong | bane to-hit, AC, defense-pool, damage multiplier consumers |
| `0x00F0` | `conditional_combat_modifier_3` | strong | bane to-hit, AC, defense-pool, damage multiplier consumers |

## Highest-priority unresolved tags

| Rank | Tag | Records | Keys | Entity-key association | DLL consumers |
|---:|---|---:|---:|---|---|
| 1 | `0x0029` | 130 | 130 | npc:130 | _NPC_DIE |
| 2 | `0x00EC` | 45 | 45 | npc:45 | _MAKE_INS_NPC1 |
| 3 | `0x0038` | 32 | 32 | room:32 | _DUMP_STORE_LIST, _SET_STPTR, _SNAPSHOT_SHOPS |
| 4 | `0x00B3` | 32 | 32 | npc:32 | _ATTACK_PVNPC |
| 5 | `0x0060` | 25 | 25 | npc:25 | _NPC_AGGRESS |
| 6 | `0x00F1` | 10 | 10 | npc:10 | _NPC_DIE, _RCI_GREET |
| 7 | `0x004B` | 9 | 9 | room:9 | _CAST_EFFECTTYPE3, _CHECK_CRIMINAL, _CREATE_WHIRLWIND, _HINT |
| 8 | `0x007E` | 7 | 7 | npc:7 | _RCI_GREET, _REQUEST_SPELL |
| 9 | `0x00F4` | 3 | 3 | room:3 | _NPC_DIE |
| 10 | `0x00CE` | 60 | 60 | item:60 | none found |
| 11 | `0x00CA` | 56 | 56 | npc:56 | _INSIGHT_RIOT |
| 12 | `0x0430` | 54 | 54 | item:54 | none found |
| 13 | `0x00B0` | 42 | 42 | npc:42 | none found |
| 14 | `0x00D7` | 33 | 33 | item:33 | none found |
| 15 | `0x0420` | 32 | 32 | room:32 | _SET_STPTR |
| 16 | `0x00C9` | 30 | 30 | door:2, room:30 | _INITIALIZE_VECTORSTUFF |
| 17 | `0x009E` | 28 | 28 | npc:28 | none found |
| 18 | `0x00B1` | 27 | 27 | npc:27 | _GET_MPMOD, _GET_ROOMBLOCKING |
| 19 | `0x00E8` | 25 | 25 | item:25 | _GET_LIGHTLEV |
| 20 | `0x042C` | 24 | 24 | room:24 | _CHECK_CRIMINAL |

## Interpretation rules

- `strong`: specific DLL consumers and/or an existing end-to-end reconciliation support the tag meaning.
- `tentative`: evidence supports a family or role, but exact semantics remain uncertain.
- `unknown`: no semantic name is assigned; records and evidence remain preserved.

Field layouts remain unresolved unless separately documented. Re-run `python scripts/analyze_mod1_tags.py` after changing the baseline or adding evidence.
