# MOD1 Tag Evidence Catalog

Phase 3 catalogs every MOD1 tag and ranks unresolved work. It does not claim that every tag or field is decoded. The ignored JSON report retains per-tag provenance, byte variability, co-occurrence, and DLL call-site line numbers.

## Coverage

- 7,060 records across 113 tag values
- 41 interpreted or hypothesized tags; 72 explicitly unresolved
- Source descriptions are excluded from both reports

## Phase 3 promotions

| Tag | Meaning | Confidence | Evidence |
|---|---|---|---|
| `0x5D` | `door_strength_or_key_rule` | tentative | PICKSTRENGTH, DOORSTRENGTH, and STEALSKEY consumers |
| `0x76` | `npc_extra_attack_slot_1` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x77` | `npc_extra_attack_slot_2` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x78` | `npc_extra_attack_slot_3` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x7A` | `npc_extra_attack_slot_5` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x7B` | `npc_extra_attack_slot_6` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x7C` | `npc_extra_attack_slot_7` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0x7D` | `npc_extra_attack_slot_8` | strong | NPC_PRE_ATTACK/GET_XTRA_ATTACK consumers |
| `0xB2` | `armor_defense_eligibility` | strong | GET_AC, GET_AC2, and GET_DPOOL consumers |
| `0xE1` | `trap_event_component_1` | strong | DO_TRAP_EVENTS consumer |
| `0xE4` | `limited_shop_stock` | strong | LIMITED_AVAILABLE, PC_BUYITEM, and shop-stock consumers |
| `0xEE` | `conditional_combat_modifier_1` | strong | bane to-hit, AC, defense-pool, damage multiplier consumers |
| `0xEF` | `conditional_combat_modifier_2` | strong | bane to-hit, AC, defense-pool, damage multiplier consumers |
| `0xF0` | `conditional_combat_modifier_3` | strong | bane to-hit, AC, defense-pool, damage multiplier consumers |

## Highest-priority unresolved tags

| Rank | Tag | Records | Keys | Entity-key association | DLL consumers |
|---:|---|---:|---:|---|---|
| 1 | `0x2F` | 3 | 3 | room:3 | _ALTER_BODY_STATS, _ATTACK_PVNPC, _AUTOCOMBAT, _CAN_MOVE |
| 2 | `0x20` | 32 | 32 | room:32 | <global>, _ALTER_BODY_STATS, _ATTACK_PVNPC, _ATTACK_PVP |
| 3 | `0x35` | 3 | 3 | room:3 | _CAN_MOVE, _CAST_EFFECTTYPE1, _CAST_EFFECTTYPE2, _CHECK_ACTIONS |
| 4 | `0x29` | 130 | 130 | npc:130 | _NPC_DIE |
| 5 | `0x21` | 18 | 18 | npc:9, room:9 | _ATTACK_PVNPC, _CLAN_INVITE, _CLAN_JOIN, _COMPILE_GAME_COUNTS |
| 6 | `0xEC` | 45 | 45 | npc:45 | _MAKE_INS_NPC1 |
| 7 | `0x38` | 32 | 32 | room:32 | _DUMP_STORE_LIST, _SET_STPTR, _SNAPSHOT_SHOPS |
| 8 | `0xB3` | 32 | 32 | npc:32 | _ATTACK_PVNPC |
| 9 | `0x60` | 25 | 25 | npc:25 | _NPC_AGGRESS |
| 10 | `0xF1` | 10 | 10 | npc:10 | _NPC_DIE, _RCI_GREET |
| 11 | `0x4B` | 9 | 9 | room:9 | _CAST_EFFECTTYPE3, _CHECK_CRIMINAL, _CREATE_WHIRLWIND, _HINT |
| 12 | `0x7E` | 7 | 7 | npc:7 | _RCI_GREET, _REQUEST_SPELL |
| 13 | `0xF4` | 3 | 3 | room:3 | _NPC_DIE |
| 14 | `0xCE` | 60 | 60 | item:60 | none found |
| 15 | `0xCA` | 56 | 56 | npc:56 | _INSIGHT_RIOT |
| 16 | `0xB0` | 42 | 42 | npc:42 | none found |
| 17 | `0xD7` | 33 | 33 | item:33 | none found |
| 18 | `0xC9` | 30 | 30 | door:2, room:30 | _INITIALIZE_VECTORSTUFF |
| 19 | `0x9E` | 28 | 28 | npc:28 | none found |
| 20 | `0xB1` | 27 | 27 | npc:27 | _GET_MPMOD, _GET_ROOMBLOCKING |

## Interpretation rules

- `strong`: specific DLL consumers and/or an existing end-to-end reconciliation support the tag meaning.
- `tentative`: evidence supports a family or role, but exact semantics remain uncertain.
- `unknown`: no semantic name is assigned; records and evidence remain preserved.

Field layouts remain unresolved unless separately documented. Re-run `python scripts/analyze_mod1_tags.py` after changing the baseline or adding evidence.
