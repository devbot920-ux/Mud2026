import {describe,expect,it} from "vitest";
import {defeatExpiresAt,defeatKey,defeatStillActive,WORLD_RESPAWN_DELAY_MS} from "../src/encounters";

describe("world encounter lifecycle",()=>{
  it("keys a defeated creature to its original spawn room",()=>expect(defeatKey(4054,4004)).toBe("4054:4004"));
  it("keeps the spawn suppressed for two minutes",()=>{const until=defeatExpiresAt(1_000);expect(until).toBe(1_000+WORLD_RESPAWN_DELAY_MS);expect(defeatStillActive(until,until-1)).toBe(true);expect(defeatStillActive(until,until)).toBe(false);});
});
