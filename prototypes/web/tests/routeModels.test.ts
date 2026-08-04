import {describe,expect,it} from "vitest";
import {TRAINING_ROUTE_MODELS,trainingRouteModel} from "../src/routeModels";

describe("modeled Pendelhaven route",()=>{
  it("covers the learning route and all nine central hub rooms",()=>expect(Object.keys(TRAINING_ROUTE_MODELS).map(Number)).toEqual([3976,3977,3978,3979,3980,3981,3982,3983,3984,4165,4166,4167,4168,4169,4170,4171,4172,4173]));
  it("uses a distinct GLB and animation treatment for each room",()=>{
    const entries=Object.values(TRAINING_ROUTE_MODELS);
    expect(new Set(entries.map(entry=>entry.path)).size).toBe(18);
    expect(new Set(entries.map(entry=>entry.animation)).size).toBe(18);
  });
  it("does not claim unmodeled rooms",()=>expect(trainingRouteModel(3985)).toBeUndefined());
});
