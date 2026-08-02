# Canonical Phase 2 Topology Audit

This report uses room identities and all topology edges from the Phase 1 canonical baseline. Derived `graph.json` data is used only for regions, coordinates, and presentation/gameplay flags. Room descriptions are excluded.

## Canonical summary

- 3,446 rooms and 7,097 source-decoded directed edges
- 49 weak components and 63 strong components
- Seed room `1` reaches 3,383 rooms; 63 remain unreachable from it
- 189 edges lack an inverse-direction counterpart
- Structural asymmetry categories: one_way_cross_region=4, one_way_door=2, one_way_hidden=1, one_way_plain=60, one_way_special_endpoint=2, one_way_vertical=14, reverse_endpoint_wrong_direction=106
- 17 reverse pairs disagree on door or hidden state
- 104 vertical edges and 49 cross-region edges

## Effect of the 20 recovered edges

The canonical baseline contains 20 semantic edges absent from the legacy graph. Exact edge tuples and source-row/byte-offset provenance are retained in the ignored machine-readable report.

| Metric | Derived graph | Canonical | Change |
|---|---:|---:|---:|
| edge records | 7,077 | 7,097 | +20 |
| duplicate node id groups | 0 | 0 | +0 |
| duplicate edge id groups | 0 | 0 | +0 |
| duplicate logical edge groups | 0 | 0 | +0 |
| dangling edges | 0 | 0 | +0 |
| unknown direction edges | 0 | 0 | +0 |
| weak components | 50 | 49 | -1 |
| strong components | 79 | 63 | -16 |
| reachable from seed | 2,918 | 3,383 | +465 |
| unreachable from seed | 528 | 63 | -465 |
| can reach seed | 2 | 2 | +0 |
| cannot reach seed | 3,444 | 3,444 | +0 |
| zero out degree rooms | 49 | 49 | +0 |
| zero in degree rooms | 63 | 58 | -5 |
| missing reverse counterparts | 169 | 189 | +20 |
| door or hidden inconsistent pairs | 17 | 17 | +0 |
| vertical edges | 104 | 104 | +0 |
| cross region edges | 47 | 49 | +2 |
| portal rooms | 5 | 5 | +0 |
| transport rooms | 41 | 41 | +0 |
| same region coordinate collisions | 184 | 184 | +0 |
| zero distance edges | 3 | 3 | +0 |

Recovered door multiedges account for most changes. In particular, the recovered links between rooms 3045 and 3046 connect the formerly separate 322-room component to the main world; the other recovered door directions substantially improve directed reachability and strong connectivity.

## Golden-fixture candidates

| Rank | Region | Name | Rooms | Score |
|---:|---|---|---:|---:|
| 1 | `R02` | Pendelhaven | 60 | 13 |
| 2 | `R18` | Imperial City | 279 | 13 |
| 3 | `R04` | Catacombs | 62 | 12 |
| 4 | `R15` | Labyrinth of Fear Level 2 | 151 | 12 |
| 5 | `R14` | Spalango | 166 | 12 |

Pendelhaven (`R02`) remains the leading fixture candidate because it ties for the highest feature score while remaining substantially smaller than Imperial City.

## Interpretation limits

The edge set is source-decoded but still based on tentative binary-offset interpretations. Regions, coordinates, and feature flags remain derived. Asymmetric links therefore remain structural findings rather than claims of gameplay intent.
