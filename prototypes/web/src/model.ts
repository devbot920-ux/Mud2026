export type Confidence = "confirmed" | "strong" | "tentative" | "unknown";
export interface Field { name: string; value: unknown; confidence: Confidence; provenance?: { source_row_id?: number; byte_offset?: number }; }
export interface Room { id: number; stable_id: string; scope: "primary" | "stub"; fields: Field[]; display?: { region?: string; region_name?: string }; provenance?: { source_row_id?: number }; }
export interface Edge { id: number; from_room: number; to_room: number; direction: string; door: boolean; hidden: boolean; provenance?: { source_row_id?: number }; }
export interface Entity { id: number; stable_id: string; fields: Field[]; }
export interface SpawnEntry { slot: number; count: number; entity_type: "npc" | "item"; entity_id: number; }
export interface Spawn { id: number; entries: SpawnEntry[]; }
export interface World { contract: { name: string; version: string }; fixture: { id: string; primary_room_ids: number[]; stub_room_ids: number[] }; rooms: Room[]; edges: Edge[]; doors: Entity[]; npcs: Entity[]; items: Entity[]; spawns: Spawn[]; modifiers: unknown[]; }

export const DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "U", "D"] as const;
export const EXPECTED_COUNTS = { rooms:63, edges:130, doors:2, npcs:18, items:12, spawns:19, modifiers:70 } as const;
const directionAliases: Record<string, string> = { n:"N", north:"N", ne:"NE", northeast:"NE", e:"E", east:"E", se:"SE", southeast:"SE", s:"S", south:"S", sw:"SW", southwest:"SW", w:"W", west:"W", nw:"NW", northwest:"NW", u:"U", up:"U", d:"D", down:"D" };

export function field<T>(entity: {fields: Field[]}, name: string, fallback: T): T {
  return (entity.fields.find((candidate) => candidate.name === name)?.value as T | undefined) ?? fallback;
}

export function validateWorld(value: unknown, exactPendelhavenCounts = true): World {
  const w = value as Partial<World>;
  const errors: string[] = [];
  if (w.contract?.name !== "mud2026.engine-neutral-world" || w.contract.version !== "1.0.0") errors.push("unsupported contract; expected mud2026.engine-neutral-world 1.0.0");
  for (const key of ["rooms", "edges", "doors", "npcs", "items", "spawns", "modifiers"] as const) if (!Array.isArray(w[key])) errors.push(`${key} must be an array`);
  if (errors.length) throw new Error(errors.join("\n"));
  const world = w as World;
  if (exactPendelhavenCounts) for (const [key, count] of Object.entries(EXPECTED_COUNTS)) {
    if ((world[key as keyof typeof EXPECTED_COUNTS] as unknown[]).length !== count) errors.push(`${key} count must be ${count}`);
  }
  const rooms = new Map(world.rooms.map((room) => [room.id, room]));
  if (rooms.size !== world.rooms.length) errors.push("room IDs must be unique");
  const primaryIds = new Set(world.fixture?.primary_room_ids ?? []); const stubIds = new Set(world.fixture?.stub_room_ids ?? []);
  if (primaryIds.size !== world.fixture.primary_room_ids.length || stubIds.size !== world.fixture.stub_room_ids.length) errors.push("fixture room lists must not contain duplicates");
  if (world.rooms.length !== primaryIds.size + stubIds.size) errors.push("room count must equal primary plus stub fixture counts");
  const edgeIds = new Set<number>();
  for (const edge of world.edges) {
    if (edgeIds.has(edge.id)) errors.push(`edge ID ${edge.id} is duplicated`); else edgeIds.add(edge.id);
    if (!rooms.has(edge.from_room) || !rooms.has(edge.to_room)) errors.push(`edge ${edge.id} has a missing endpoint`);
    if (!DIRECTIONS.includes(edge.direction as typeof DIRECTIONS[number])) errors.push(`edge ${edge.id} has unknown direction ${edge.direction}`);
  }
  const npcs = new Set(world.npcs.map((x) => x.id)); const items = new Set(world.items.map((x) => x.id));
  if (npcs.size !== world.npcs.length || items.size !== world.items.length) errors.push("NPC and item IDs must be unique within their families");
  for (const spawn of world.spawns) for (const entry of spawn.entries) {
    if (entry.entity_type !== "npc" && entry.entity_type !== "item") errors.push(`spawn ${spawn.id} has unknown entity type ${String(entry.entity_type)}`);
    else if (!(entry.entity_type === "npc" ? npcs : items).has(entry.entity_id)) errors.push(`spawn ${spawn.id} references missing ${entry.entity_type} ${entry.entity_id}`);
  }
  for (const id of world.fixture.primary_room_ids) if (rooms.get(id)?.scope !== "primary") errors.push(`primary fixture room ${id} is absent or not primary`);
  for (const id of world.fixture.stub_room_ids) if (rooms.get(id)?.scope !== "stub") errors.push(`stub fixture room ${id} is absent or not stub`);
  if (errors.length) throw new Error(errors.join("\n"));
  return world;
}

export function edgesFrom(world: World, roomId: number, showHidden = false): Edge[] {
  return world.edges.filter((edge) => edge.from_room === roomId && (showHidden || !edge.hidden));
}

export function commandDirection(command: string): string | undefined { return directionAliases[command.trim().toLowerCase()]; }

export function travel(world: World, roomId: number, command: string, showHidden = false): Edge | undefined {
  const direction = commandDirection(command); if (!direction) return undefined;
  return edgesFrom(world, roomId, showHidden).find((edge) => edge.direction === direction);
}
