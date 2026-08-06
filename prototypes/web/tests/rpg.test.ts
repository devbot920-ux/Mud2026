import {describe,expect,it} from "vitest";
import {EQUIPMENT,attackDamage,characterStats,findEquipment,gainExperience,receivedDamage,rewardForMob,updateEndurance} from "../src/rpg";

describe("character races and classes",()=>{
  it("creates meaningfully different builds",()=>{expect(characterStats("Dwarf","Warrior").maxHealth).toBeGreaterThan(characterStats("Elf","Mage").maxHealth);expect(characterStats("Kobold","Rogue").maxEndurance).toBeGreaterThan(characterStats("Human","Warrior").maxEndurance);});
  it("scales health and damage with level",()=>{expect(characterStats("Human","Warrior",3).maxHealth).toBeGreaterThan(characterStats("Human","Warrior",1).maxHealth);expect(characterStats("Human","Mage",3).baseDamage).toBeGreaterThan(characterStats("Human","Mage",1).baseDamage);});
});

describe("progression and equipment",()=>{
  it("handles multiple level gains and carries excess experience",()=>expect(gainExperience({level:1,experience:90,nextLevelExperience:100},220)).toEqual({progression:{level:3,experience:10,nextLevelExperience:300},levelsGained:2}));
  it("adds weapon damage and reduces incoming damage with armor",()=>{const stats=characterStats("Human","Warrior");expect(attackDamage(stats,EQUIPMENT["guard-hammer"])).toBe(18);expect(receivedDamage(10,stats,EQUIPMENT["thug-jerkin"])).toBe(5);});
  it("provides deterministic rewards for every hostile archetype",()=>{expect(rewardForMob(4003)?.loot).toBe("slug-hide");expect(rewardForMob(4006)?.experience).toBeGreaterThan(rewardForMob(129)!.experience);});
  it("finds equipment by player-facing name",()=>expect(findEquipment("kobold guard hammer")?.id).toBe("guard-hammer"));
  it("drains endurance while running and recovers it while resting",()=>{expect(updateEndurance(100,100,1,true,true)).toBe(82);expect(updateEndurance(82,100,1,false,false)).toBe(93);});
});
