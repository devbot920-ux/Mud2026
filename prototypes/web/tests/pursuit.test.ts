import {describe,expect,it} from "vitest";
import {canMobFollow,chaseStep,exitBlocked} from "../src/pursuit";
describe("hostile pursuit",()=>{
  it("follows only ordinary edges inside the fixture",()=>{expect(canMobFollow({to_room:2},[1,2])).toBe(true);expect(canMobFollow({to_room:2,hidden:true},[1,2])).toBe(false);expect(canMobFollow({to_room:3},[1,2])).toBe(false);});
  it("blocks a nearby exit unless the player sprints",()=>{expect(exitBlocked({x:0,z:0},{x:2,z:0},true,false)).toBe(true);expect(exitBlocked({x:0,z:0},{x:2,z:0},true,true)).toBe(false);});
  it("moves without overshooting",()=>expect(chaseStep({x:0,z:0},{x:3,z:4},2,1)).toEqual({x:1.2,z:1.6}));
});
