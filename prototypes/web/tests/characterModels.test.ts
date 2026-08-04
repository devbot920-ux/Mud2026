import {describe,expect,it} from "vitest";
import {TUTORIAL_CHARACTER_MODELS,tutorialCharacterModel} from "../src/characterModels";

describe("tutorial character models",()=>{
  it("covers every canonical NPC and mob on the modeled route",()=>expect(Object.keys(TUTORIAL_CHARACTER_MODELS).map(Number)).toEqual([3993,3994,3995,3996,3997,3998]));
  it("gives each character a full model and individual idle treatment",()=>{
    const entries=Object.values(TUTORIAL_CHARACTER_MODELS);
    expect(new Set(entries.map(entry=>entry.path)).size).toBe(6);
    expect(new Set(entries.map(entry=>entry.animation)).size).toBe(6);
  });
  it("keeps unknown entities on the generic marker fallback",()=>expect(tutorialCharacterModel(1)).toBeUndefined());
});
