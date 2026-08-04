import {describe,expect,it} from "vitest";
import {constrainModeledMovement,entrySpawnAfterTravel,horizontalTriggerReached,modeledFloorHeight} from "../src/navigation";

describe("room entry placement",()=>{
  it("enters westward travel at the new room's east door facing inward",()=>{const spawn=entrySpawnAfterTravel("W")!;expect(spawn.incomingDirection).toBe("E");expect(spawn.x).toBeGreaterThan(6);expect(spawn.yaw).toBeCloseTo(Math.PI/2);});
  it("handles diagonal incoming doors",()=>expect(entrySpawnAfterTravel("NW")?.incomingDirection).toBe("SE"));
  it("uses the authoritative return direction when the graph is not geometrically inverse",()=>{const spawn=entrySpawnAfterTravel("W","W")!;expect(spawn.incomingDirection).toBe("W");expect(spawn.x).toBeLessThan(-6);});
  it("places upward travel beside the down route",()=>{const spawn=entrySpawnAfterTravel("U")!;expect(spawn.incomingDirection).toBe("D");expect(spawn.x).toBeLessThan(0);expect(spawn.z).toBeGreaterThan(0);});
  it("places downward travel beside the up route",()=>expect(entrySpawnAfterTravel("D")?.incomingDirection).toBe("U"));
  it("rejects unknown directions",()=>expect(entrySpawnAfterTravel("SIDEWAYS")).toBeUndefined());
  it("reaches vertical exits by horizontal proximity",()=>expect(horizontalTriggerReached({x:4,z:-4},{x:4,z:-4})).toBe(true));
  it("spawns outside the immediate vertical return trigger",()=>{const spawn=entrySpawnAfterTravel("U")!;expect(horizontalTriggerReached(spawn,{x:-4,z:4})).toBe(false);});
});

describe("modeled geometry movement",()=>{
  it("raises the player smoothly while climbing the enlightenment dais",()=>expect(modeledFloorHeight(3983,{x:3,z:-3})).toBeGreaterThan(.7));
  it("keeps ordinary floors level",()=>expect(modeledFloorHeight(4165,{x:4,z:4})).toBe(0));
  it("blocks walking through the advancement altar",()=>expect(constrainModeledMovement(3984,{x:3,z:0},{x:2,z:0})).toEqual({x:3,z:0}));
  it("allows movement beside the altar",()=>expect(constrainModeledMovement(3984,{x:4,z:2},{x:4,z:1})).toEqual({x:4,z:1}));
});
