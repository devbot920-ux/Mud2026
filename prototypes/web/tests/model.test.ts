import { describe, expect, it } from "vitest";
import { edgesFrom, travel, validateWorld, type World } from "../src/model";

function fixture(): World {
  const f=(name:string,value:unknown)=>({name,value,confidence:"strong" as const});
  return {
    contract:{name:"mud2026.engine-neutral-world",version:"1.0.0"}, fixture:{id:"synthetic",primary_room_ids:[4057,4058],stub_room_ids:[9]},
    rooms:[{id:4057,stable_id:"room:4057",scope:"primary",fields:[f("short_description","Test A")]},{id:4058,stable_id:"room:4058",scope:"primary",fields:[]},{id:9,stable_id:"room:9",scope:"stub",fields:[]}],
    edges:[
      {id:1,from_room:4057,to_room:4058,direction:"W",door:true,hidden:false},
      {id:2,from_room:4058,to_room:4057,direction:"W",door:false,hidden:false},
      {id:3,from_room:4057,to_room:9,direction:"W",door:false,hidden:false},
      {id:4,from_room:4057,to_room:9,direction:"U",door:false,hidden:true},
    ], doors:[],npcs:[{id:20,stable_id:"npc:20",fields:[]}],items:[{id:30,stable_id:"item:30",fields:[]}],spawns:[{id:4057,entries:[{slot:1,count:1,entity_type:"npc",entity_id:20},{slot:2,count:1,entity_type:"item",entity_id:30}]}],modifiers:[]
  };
}

describe("world contract",()=>{
  it("validates a fixture with parallel and same-west edges",()=>{const w=validateWorld(fixture());expect(edgesFrom(w,4057)).toHaveLength(2);expect(edgesFrom(w,4057).map(e=>e.direction)).toEqual(["W","W"]);expect(edgesFrom(w,4058)[0].direction).toBe("W");});
  it("suppresses hidden edges until requested",()=>{const w=fixture();expect(edgesFrom(w,4057).some(e=>e.hidden)).toBe(false);expect(edgesFrom(w,4057,true).some(e=>e.hidden)).toBe(true);});
  it("uses authoritative first parallel edge for a command",()=>expect(travel(fixture(),4057,"west")?.id).toBe(1));
  it("supports vertical and abbreviated commands",()=>expect(travel(fixture(),4057,"u",true)?.id).toBe(4));
  it("rejects dangling edges",()=>{const w=fixture();w.edges[0].to_room=999;expect(()=>validateWorld(w)).toThrow(/missing endpoint/);});
  it("rejects dangling spawn references",()=>{const w=fixture();w.spawns[0].entries[0].entity_id=999;expect(()=>validateWorld(w)).toThrow(/missing npc/);});
  it("rejects a contract version change",()=>{const w=fixture();w.contract.version="2.0.0";expect(()=>validateWorld(w)).toThrow(/unsupported contract/);});
  it("rejects a fixture count mismatch",()=>{const w=fixture();w.fixture.stub_room_ids=[];expect(()=>validateWorld(w)).toThrow(/room count/);});
});
