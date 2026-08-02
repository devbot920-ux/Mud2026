# Phase 2 Topology Audit

This report is generated from the configured `derived_graph` source. The source was read only. Room descriptions are intentionally excluded.

## Summary

- 3,446 node records (3,446 unique IDs)
- 7,077 directed edge records (7,077 with valid endpoints)
- 0 duplicate node-ID groups; 0 duplicate edge-ID groups
- 0 dangling edges; 0 edges with unknown directions
- 50 weak components; 79 strong components
- 169 directed edges lack an inverse-direction counterpart
- Structural asymmetry categories: one_way_cross_region=4, one_way_door=14, one_way_hidden=1, one_way_plain=65, one_way_special_endpoint=2, one_way_vertical=14, reverse_endpoint_wrong_direction=69
- 17 reverse pairs disagree on door or hidden state
- 104 vertical edges; 47 cross-region edges
- 5 portal-flagged rooms; 41 transport-flagged rooms
- 184 same-region coordinate collisions; 3 zero-distance edges

## Reachability

The deterministic seed is room `1` (the natural-lowest ID in the largest weak component). It reaches 2,918 rooms; 528 rooms are not reachable from it by directed links.

## Golden-fixture candidates

Scores award practicality points by room count plus one point for each topology/gameplay feature category present. This is a candidate ranking, not a final selection.

| Rank | Region | Name | Rooms | Score | Present categories |
|---:|---|---|---:|---:|---|
| 1 | `R02` | Pendelhaven | 60 | 13 | door_edges, hidden_edges, vertical_edges, diagonal_edges, transport_rooms, store_rooms, tavern_rooms, quest_rooms, spawn_rooms, cross_region_edges |
| 2 | `R18` | Imperial City | 279 | 13 | hidden_edges, vertical_edges, diagonal_edges, portal_rooms, transport_rooms, store_rooms, tavern_rooms, quest_rooms, trainer_rooms, spawn_rooms, cross_region_edges |
| 3 | `R04` | Catacombs | 62 | 12 | door_edges, hidden_edges, vertical_edges, diagonal_edges, transport_rooms, quest_rooms, trap_rooms, spawn_rooms, cross_region_edges |
| 4 | `R15` | Labyrinth of Fear Level 2 | 151 | 12 | door_edges, hidden_edges, vertical_edges, diagonal_edges, transport_rooms, quest_rooms, trap_rooms, spawn_rooms, cross_region_edges |
| 5 | `R14` | Spalango | 166 | 12 | hidden_edges, vertical_edges, diagonal_edges, transport_rooms, store_rooms, quest_rooms, trainer_rooms, spawn_rooms, cross_region_edges |
| 6 | `R20` | Ice Dale Caverns | 235 | 12 | door_edges, vertical_edges, diagonal_edges, transport_rooms, quest_rooms, trainer_rooms, trap_rooms, spawn_rooms, cross_region_edges |
| 7 | `R17` | Labyrinth of Fear Level 1 | 245 | 12 | door_edges, hidden_edges, vertical_edges, diagonal_edges, transport_rooms, quest_rooms, trap_rooms, spawn_rooms, cross_region_edges |
| 8 | `R11` | South City Forest | 637 | 12 | door_edges, hidden_edges, vertical_edges, diagonal_edges, transport_rooms, store_rooms, quest_rooms, trainer_rooms, trap_rooms, spawn_rooms, cross_region_edges |
| 9 | `R10` | Catacombs 2 | 67 | 11 | door_edges, hidden_edges, vertical_edges, diagonal_edges, transport_rooms, trap_rooms, spawn_rooms, cross_region_edges |
| 10 | `R12` | Orc Caves | 150 | 11 | door_edges, hidden_edges, diagonal_edges, transport_rooms, quest_rooms, trap_rooms, spawn_rooms, cross_region_edges |

## Interpretation limits

Coordinates and region membership are derived presentation data, not original world facts. Phase 1 provenance import and baseline reconciliation are still incomplete, so this audit cannot determine whether asymmetric links or flag disagreements are intentional. The detailed machine-readable report is generated under ignored `var/reports/topology-audit.json`.
