# Phase 4 Golden Fixture Export

Phase 4 defines export contract `mud2026.engine-neutral-world` version `1.0.0` and a closed Pendelhaven fixture. The tracked JSON Schema is `schema/engine-neutral-export-v1.schema.json`; generated game data remains private under ignored `var/exports/`.

## Boundary

The primary boundary is exactly the 60 rooms assigned to derived region `R02`: `3976`–`3984`, `4020`–`4060`, and `4165`–`4174`. Region membership and coordinates are presentation-derived evidence, not source-authored facts.

Every canonical edge touching a primary room is retained. An endpoint outside `R02` becomes a skeletal, non-expanding stub. This adds rooms `416` (Imperial City), `958` (Imperial Guild), and `4061` (sewers). Their other edges, fields, modifiers, and region content are intentionally excluded.

The resulting topology has 125 primary-to-primary edges and five boundary crossings. All 130 directed edge records retain their canonical IDs and source offsets. Parallel edges and the two door-side records remain separate. In particular, the door records between `4057` and `4058` decode as `W` in both directions; the exporter does not invent an inverse direction.

## Content closure

| Collection | Records |
|---|---:|
| Primary rooms | 60 |
| Boundary room stubs | 3 |
| Directed multiedges | 130 |
| Door-side records | 2 |
| Room spawn records | 19 |
| Spawn entries | 32 |
| Referenced NPCs | 18 |
| Referenced items | 12 |
| Non-base MOD1 modifiers | 70 |

All NPC and item spawn references resolve. The 70 modifiers comprise every non-base MOD1 row sharing a key with a primary room or referenced NPC/item: 21 have current tag interpretations and 49 remain unresolved. Each retains its complete raw record in Base64, source-row provenance, tag, confidence, and optional working meaning. Raw records and source descriptions exist only in the ignored private export.

## Contract rules

- Entities use stable numeric IDs and carry decoded fields individually with evidence source row, offsets, decoding rule, and confidence.
- Edges form a directed multigraph and are identified by canonical `topology_edge_id`.
- Door sides are records, not synthesized physical door pairs.
- Spawns reference typed NPC/item entities; unknown entry types remain representable.
- Display region and coordinates are explicitly classified as derived.
- Unknown modifier tags and bytes are preserved without assigning invented meanings.
- Item identities are unique: the corrected little-endian `u16` MOD1 tag distinguishes 529 true `0x0032` item bases from 20 unrelated `0x0432` modifiers.

## Commands

```powershell
python scripts/export_golden_fixture.py
python scripts/serve_fixture_viewer.py
```

The exporter writes `var/exports/pendelhaven-v1.json` atomically. The viewer is a read-only, engine-neutral inspection page and contains no source content itself.

## Verification

Tests cover exact one-hop boundary behavior, directed multiedges, door/NPC/item/spawn closure, dangling references, raw unknown modifier preservation, contract identity, deterministic output, and atomic replacement. The exporter reads the canonical baseline with SQLite immutable/query-only settings.
