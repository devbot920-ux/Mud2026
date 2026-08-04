import {describe,expect,it} from "vitest";
import {PENDELHAVEN_CHARACTER_MODELS,TUTORIAL_CHARACTER_MODELS,characterModel} from "../src/characterModels";

describe("tutorial character models",()=>{
  it("covers every canonical NPC and mob on the modeled route",()=>expect(Object.keys(TUTORIAL_CHARACTER_MODELS).map(Number)).toEqual([3993,3994,3995,3996,3997,3998]));
  it("gives each character a full model and individual idle treatment",()=>{
    const entries=Object.values(TUTORIAL_CHARACTER_MODELS);
    expect(new Set(entries.map(entry=>entry.path)).size).toBe(6);
    expect(new Set(entries.map(entry=>entry.animation)).size).toBe(6);
  });
  it("covers all central NPCs and four extracted arena opponents",()=>expect(Object.keys(PENDELHAVEN_CHARACTER_MODELS).map(Number).sort((a,b)=>a-b)).toEqual([129,4003,4004,4006,4175,4176,4177,4178,4179,4180,4181,4182]));
  it("keeps unknown entities on the generic marker fallback",()=>expect(characterModel(1)).toBeUndefined());
});
