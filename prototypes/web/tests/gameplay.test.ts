import {describe,expect,it} from "vitest";
import {findFacingEntity,gameplayCommand,practiceDamage} from "../src/gameplay";

describe("generic gaze inspection",()=>{
  const entities=[{id:72,x:2,z:-2},{id:3998,x:-2,z:-2}];
  it("selects the closest entity under the reticle",()=>expect(findFacingEntity({x:2,z:0},{x:0,z:-1},entities)?.id).toBe(72));
  it("requires proximity and facing",()=>{
    expect(findFacingEntity({x:2,z:0},{x:0,z:1},entities)).toBeUndefined();
    expect(findFacingEntity({x:20,z:20},{x:0,z:-1},entities)).toBeUndefined();
  });
});

describe("knife and practice combat commands",()=>{
  it.each([["get knife","get-knife"],["pick up a knife","get-knife"],["attack dummy","attack-dummy"],["a wooden dummy","attack-dummy"],["stop","stop-combat"],["i","inventory"]])("maps %s",(raw,expected)=>expect(gameplayCommand(raw)).toBe(expected));
  it("leaves travel commands alone",()=>expect(gameplayCommand("north")).toBeUndefined());
  it("makes the knife improve practice damage",()=>{expect(practiceDamage(false)).toBe(2);expect(practiceDamage(true)).toBe(5);});
});
