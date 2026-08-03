export interface Point2 { x: number; z: number }

export type InitialRoomTarget = "old-man" | "parchment";
export type InitialRoomAction = "look-room" | "inspect-old-man" | "talk-old-man" | "read-parchment" | "take-parchment";

export const INITIAL_ROOM_ID = 3976;
export const INITIAL_ROOM_INTERACTIONS: ReadonlyArray<{ target: InitialRoomTarget; label: string; position: Point2 }> = [
  { target: "old-man", label: "old man", position: { x: 2.7, z: -7.15 } },
  { target: "parchment", label: "old parchment", position: { x: -2.6, z: -8.55 } },
];

/** Keep the player inside the chamber. The west trigger sits just inside this boundary. */
export function constrainInitialRoomMovement(proposed: Point2): Point2 {
  return {
    x: Math.max(-8.45, Math.min(8.45, proposed.x)),
    z: Math.max(-8.45, Math.min(8.45, proposed.z)),
  };
}

export function findInitialRoomTarget(position: Point2, forward: Point2, maxDistance = 3.25): InitialRoomTarget | undefined {
  const forwardLength = Math.hypot(forward.x, forward.z);
  if (forwardLength < 0.001) return undefined;
  let best: { target: InitialRoomTarget; distance: number } | undefined;
  for (const interaction of INITIAL_ROOM_INTERACTIONS) {
    const dx = interaction.position.x - position.x;
    const dz = interaction.position.z - position.z;
    const distance = Math.hypot(dx, dz);
    if (distance > maxDistance || distance < 0.001) continue;
    const facing = (dx * forward.x + dz * forward.z) / (distance * forwardLength);
    if (facing < 0.55) continue;
    if (!best || distance < best.distance) best = { target: interaction.target, distance };
  }
  return best?.target;
}

export function initialRoomCommand(raw: string): InitialRoomAction | undefined {
  const words = raw.trim().toLowerCase().replace(/\s+/g, " ");
  if (["look", "l", "look room", "look around"].includes(words)) return "look-room";
  if (/^(look( at)?|examine|inspect) (the )?(old )?man$/.test(words)) return "inspect-old-man";
  if (/^(talk( to)?|speak( to)?) (the )?(old )?man$/.test(words)) return "talk-old-man";
  if (/^(look( at)?|examine|inspect|read) (the )?(old )?parchment$/.test(words)) return "read-parchment";
  if (/^(take|get|remove) (the )?(old )?parchment$/.test(words)) return "take-parchment";
  return undefined;
}
