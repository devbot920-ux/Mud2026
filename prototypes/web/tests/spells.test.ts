import {describe,expect,it} from "vitest";
import {castingBonus,castingThreshold,recoverySeconds,rollDice,spellMagnitude,type RoseSpell} from "../src/spells";

const spell=(partial:Partial<RoseSpell>):RoseSpell=>({id:71,name:"Test bolt",abbreviation:"testbolt",sphere:1,sphere_name:"Forces",secondary_sphere:0,learning_threshold:20,proficiency_requirement:32,secondary_requirement:0,mana_cost:20,effect_type:1,base_recovery:6,parser_kind:1,effects:[{handler:0,dice_count:2,roll_min:2,roll_max:16}],target_flags:[0,0,0,0,0],damage_type:8,...partial});
describe("recovered Rose spell rules",()=>{
  it("uses the recovered walk casting bonus",()=>{expect(castingBonus("Mage",4)).toBe(8);expect(castingBonus("Priest",4)).toBe(8);expect(castingBonus("Scholar",4)).toBe(4);expect(castingBonus("Warrior",4)).toBe(0);});
  it("uses 85 + casting bonus + proficiency delta",()=>expect(castingThreshold(spell({}),{1:40},"Mage",2)).toBe(97));
  it("rolls each inclusive damage die",()=>expect(rollDice(2,2,16,()=>0)).toBe(4));
  it("matches source spell damage ranges",()=>{expect(spellMagnitude(spell({}),1,()=>0)).toBe(4);expect(spellMagnitude(spell({}),1,()=>.999)).toBe(32);expect(spellMagnitude(spell({name:"Shock",effects:[{handler:0,dice_count:4,roll_min:10,roll_max:30}]}),1,()=>.999)).toBe(120);});
  it("scales healing roll count by caster level",()=>expect(spellMagnitude(spell({effects:[{handler:1,dice_count:25,roll_min:100,roll_max:0}]}),3,()=>0)).toBe(75));
  it("keeps approximate recovery bounded",()=>expect(recoverySeconds(spell({}),100)).toBeCloseTo(3.6));
});
