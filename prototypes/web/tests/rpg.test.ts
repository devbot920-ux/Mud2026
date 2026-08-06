import {describe,expect,it} from "vitest";
import {EQUIPMENT,attackDamage,characterAttributes,characterSkills,characterStats,equip,findEquipment,gainExperience,inventoryWeight,receivedDamage,resolveMeleeAttack,rewardForMob,unequip,updateEndurance} from "../src/rpg";

describe("source-aligned character rules",()=>{
  it("models all eight Rose attributes",()=>expect(Object.keys(characterAttributes("Human","Archtypical"))).toHaveLength(8));
  it("reflects race and walk-of-life strengths",()=>{expect(characterAttributes("Giant","Warrior").strength).toBeGreaterThan(characterAttributes("Fairfolk","Mage").strength);expect(characterAttributes("Elf","Gypsy").perception).toBeGreaterThan(characterAttributes("Human","Archtypical").perception);});
  it("derives health, mana, movement, encumbrance, and attack delay",()=>{const tough=characterStats("Dwarf","Warrior"),quick=characterStats("Fairfolk","Gypsy");expect(tough.maxHealth).toBeGreaterThan(quick.maxHealth);expect(quick.attackInterval).toBeLessThan(tough.attackInterval);expect(tough.carryCapacity).toBeGreaterThan(0);});
  it("adjusts proficiencies using their prime attributes",()=>{const skills=characterSkills("Giant","Warrior");expect(skills.find(skill=>skill.name==="Melee weaponry")!.adjusted).toBeGreaterThan(skills.find(skill=>skill.name==="Magical defense")!.adjusted);});
  it("scales health and damage with level",()=>{expect(characterStats("Human","Warrior",3).maxHealth).toBeGreaterThan(characterStats("Human","Warrior",1).maxHealth);expect(characterStats("Human","Mage",3).baseDamage).toBeGreaterThan(characterStats("Human","Mage",1).baseDamage);});
});

describe("progression and inventory",()=>{
  it("uses a proficiency d100 gate and ranged weapon roll",()=>{const hit=resolveMeleeAttack("Human","Warrior",1,EQUIPMENT["training-knife"],0,0,()=>0);expect(hit.hit).toBe(true);expect(hit.damage).toBeGreaterThanOrEqual(3);const miss=resolveMeleeAttack("Human","Warrior",1,EQUIPMENT["guard-hammer"],10,0,()=>.999);expect(miss.hit).toBe(false);});
  it("handles multiple level gains and carries excess experience",()=>expect(gainExperience({level:1,experience:90,nextLevelExperience:100},220)).toEqual({progression:{level:3,experience:10,nextLevelExperience:300},levelsGained:2}));
  it("adds weapon damage and reduces incoming damage with armor",()=>{const stats=characterStats("Human","Warrior");expect(attackDamage(stats,EQUIPMENT["guard-hammer"])).toBe(stats.baseDamage+12);expect(receivedDamage(10,stats,EQUIPMENT["thug-jerkin"])).toBe(5);});
  it("tracks carried weight and one equipped item per slot",()=>{expect(inventoryWeight(["training-knife","thug-jerkin"])).toBe(15);const armed=equip({},EQUIPMENT["training-knife"]);expect(equip(armed,EQUIPMENT["guard-hammer"]).weapon).toBe("guard-hammer");expect(unequip(armed,"weapon").weapon).toBeUndefined();});
  it("provides deterministic rewards for every hostile archetype",()=>{expect(rewardForMob(4003)?.loot).toBe("slug-hide");expect(rewardForMob(4006)?.experience).toBeGreaterThan(rewardForMob(129)!.experience);});
  it("finds equipment by player-facing name",()=>expect(findEquipment("kobold guard hammer")?.id).toBe("guard-hammer"));
  it("drains movement endurance while running and recovers it while resting",()=>{expect(updateEndurance(100,100,1,true,true)).toBe(82);expect(updateEndurance(82,100,1,false,false)).toBe(93);});
});
