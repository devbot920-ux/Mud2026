import {describe,expect,it} from "vitest";
import {ARENA_ROSTER,arenaOpponent,hostileStats,matchesHostileName,playerDamage,shouldAutoAggro,sourceBehavior} from "../src/combat";

describe("Pendelhaven arena combat",()=>{
  it("cycles deterministically through every extracted hostile model",()=>expect([0,1,2,3,4].map(arenaOpponent)).toEqual([...ARENA_ROSTER,ARENA_ROSTER[0]]));
  it("gives tougher opponents more health and damage",()=>{expect(hostileStats(4006)!.maxHealth).toBeGreaterThan(hostileStats(129)!.maxHealth);expect(hostileStats(4006)!.damage).toBeGreaterThan(hostileStats(4003)!.damage);});
  it("marks all current behavior-1 source mobs as auto aggressive",()=>expect(ARENA_ROSTER.every(shouldAutoAggro)).toBe(true));
  it("preserves the decoded behavior meanings",()=>expect([sourceBehavior(1),sourceBehavior(2),sourceBehavior(0)]).toEqual(["aggressive","criminals-only","passive"]));
  it("recognizes canonical and convenient target names",()=>{expect(matchesHostileName(4003,"slug")).toBe(true);expect(matchesHostileName(4004,"kobold thug")).toBe(true);expect(matchesHostileName(129,"opponent")).toBe(true);});
  it("makes the training knife useful",()=>expect(playerDamage(true)).toBeGreaterThan(playerDamage(false)));
});
