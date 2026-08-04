import {describe,expect,it} from "vitest";
import {TRAINING_ROUTE_MODELS,trainingRouteModel} from "../src/routeModels";

describe("modeled training route",()=>{
  it("covers every room from the start through the completion altar",()=>expect(Object.keys(TRAINING_ROUTE_MODELS).map(Number)).toEqual([3976,3977,3978,3979,3980,3981,3982,3983,3984]));
  it("uses a distinct GLB and animation treatment for each room",()=>{
    const entries=Object.values(TRAINING_ROUTE_MODELS);
    expect(new Set(entries.map(entry=>entry.path)).size).toBe(9);
    expect(new Set(entries.map(entry=>entry.animation)).size).toBe(9);
  });
  it("does not claim unmodeled rooms",()=>expect(trainingRouteModel(3985)).toBeUndefined());
});
