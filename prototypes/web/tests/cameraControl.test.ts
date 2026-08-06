import {describe,expect,it} from "vitest";
import {MAX_THIRD_PERSON_DISTANCE,MIN_THIRD_PERSON_DISTANCE,adjustThirdPersonDistance} from "../src/cameraControl";

describe("third-person camera zoom",()=>{
  it("moves closer when the wheel is scrolled upward",()=>expect(adjustThirdPersonDistance(5.8,-100)).toBeLessThan(5.8));
  it("moves farther away when the wheel is scrolled downward",()=>expect(adjustThirdPersonDistance(5.8,100)).toBeGreaterThan(5.8));
  it("clamps the camera to safe limits",()=>{expect(adjustThirdPersonDistance(3,-10000)).toBe(MIN_THIRD_PERSON_DISTANCE);expect(adjustThirdPersonDistance(8,10000)).toBe(MAX_THIRD_PERSON_DISTANCE);});
});
