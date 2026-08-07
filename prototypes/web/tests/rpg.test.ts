import {describe,expect,it} from "vitest";
import {EQUIPMENT,EQUIPMENT_SLOTS,attackDamage,canPromote,characterAttributes,characterSkills,characterStats,equip,equipmentArmor,findEquipment,gainExperience,inventoryWeight,promote,receivedDamage,resolveMeleeAttack,restRecovery,rewardForMob,skillTrainingCost,unequip,updateEndurance} from "../src/rpg";

describe("source-aligned character rules",()=>{
  it("models all eight Rose attributes",()=>expect(Object.keys(characterAttributes("Human","Archtypical"))).toHaveLength(8));
  it("reflects race and walk-of-life strengths",()=>{expect(characterAttributes("Giant","Warrior").strength).toBeGreaterThan(characterAttributes("Fairfolk","Mage").strength);expect(characterAttributes("Elf","Gypsy").perception).toBeGreaterThan(characterAttributes("Human","Archtypical").perception);});
  it("derives health, mana, movement, encumbrance, and attack delay",()=>{const tough=characterStats("Dwarf","Warrior"),quick=characterStats("Fairfolk","Gypsy");expect(tough.maxHealth).toBeGreaterThan(quick.maxHealth);expect(quick.attackInterval).toBeLessThan(tough.attackInterval);expect(tough.carryCapacity).toBeGreaterThan(0);});
  it("adjusts proficiencies using their prime attributes",()=>{const skills=characterSkills("Giant","Warrior");expect(skills.find(skill=>skill.name==="Melee weaponry")!.adjusted).toBeGreaterThan(skills.find(skill=>skill.name==="Magical defense")!.adjusted);});
  it("scales health and damage with level",()=>{expect(characterStats("Human","Warrior",3).maxHealth).toBeGreaterThan(characterStats("Human","Warrior",1).maxHealth);expect(characterStats("Human","Mage",3).baseDamage).toBeGreaterThan(characterStats("Human","Mage",1).baseDamage);});
  it("makes trained strength increase physical damage",()=>expect(characterStats("Human","Warrior",1,{strength:5}).baseDamage).toBeGreaterThan(characterStats("Human","Warrior").baseDamage));
});

describe("progression and inventory",()=>{
  it("uses a proficiency d100 gate and ranged weapon roll",()=>{const hit=resolveMeleeAttack("Human","Warrior",1,EQUIPMENT["training-knife"],0,0,()=>0);expect(hit.hit).toBe(true);expect(hit.damage).toBeGreaterThanOrEqual(3);const miss=resolveMeleeAttack("Human","Warrior",1,EQUIPMENT["guard-hammer"],10,0,()=>.999);expect(miss.hit).toBe(false);});
  it("banks experience until explicit promotion",()=>{const earned=gainExperience({level:1,experience:90,nextLevelExperience:100},220);expect(earned).toEqual({level:1,experience:310,nextLevelExperience:100});expect(canPromote(earned)).toBe(true);const advanced=promote(earned,()=>0);expect(advanced).toEqual({progression:{level:2,experience:210,nextLevelExperience:200},developmentPoints:51,attributePoints:2});});
  it("adds weapon damage and reduces incoming damage with armor",()=>{const stats=characterStats("Human","Warrior");expect(attackDamage(stats,EQUIPMENT["guard-hammer"])).toBe(stats.baseDamage+12);expect(receivedDamage(10,stats,EQUIPMENT["thug-jerkin"])).toBe(5);});
  it("tracks carried weight and one equipped item per slot",()=>{expect(inventoryWeight(["training-knife","thug-jerkin"])).toBe(15);const armed=equip({},EQUIPMENT["training-knife"]);expect(equip(armed,EQUIPMENT["guard-hammer"]).weapon).toBe("guard-hammer");expect(unequip(armed,"weapon").weapon).toBeUndefined();});
  it("models the weapon and twelve recovered wearable locations",()=>{expect(EQUIPMENT_SLOTS).toHaveLength(13);expect(EQUIPMENT_SLOTS).toEqual(expect.arrayContaining(["torso","arms","legs","feet","head","shield","cloak","left-ring","right-ring","necklace","bracers","amulet"]));expect(equipmentArmor(["thug-jerkin","slug-hide","animal-hide-boots"])).toBe(6);});
  it("raises training cost by proficiency and applies trained ranks",()=>{expect(skillTrainingCost("Warrior","Melee weaponry",18)).toBe(3);expect(skillTrainingCost("Warrior","Melee weaponry",40)).toBe(4);expect(characterSkills("Human","Warrior",{}, {"Melee weaponry":2})[0].raw).toBe(20);});
  it("provides deterministic rewards for every hostile archetype",()=>{expect(rewardForMob(4003)?.loot).toBe("slug-hide");expect(rewardForMob(4006)?.experience).toBeGreaterThan(rewardForMob(129)!.experience);});
  it("finds equipment by player-facing name",()=>expect(findEquipment("kobold guard hammer")?.id).toBe("guard-hammer"));
  it("drains movement endurance while running and recovers it while resting",()=>{expect(updateEndurance(100,100,1,true,true)).toBe(82);expect(updateEndurance(82,100,1,false,false)).toBe(93);});
  it("restores health without exceeding maximum",()=>{expect(restRecovery(40,100,10,36)).toBe(60);expect(restRecovery(95,100,10,36)).toBe(100);});
});
