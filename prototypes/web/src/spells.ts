import type {PlayerClass} from "./rpg";

export interface SpellEffect {handler:number;dice_count:number;roll_min:number;roll_max:number}
export interface RoseSpell {id:number;name:string;abbreviation:string;sphere:number;sphere_name:string;secondary_sphere:number;learning_threshold:number;proficiency_requirement:number;secondary_requirement:number;mana_cost:number;effect_type:number;base_recovery:number;parser_kind:number;effects:SpellEffect[];target_flags:number[];damage_type:number}
export interface SpellFixture {contract:{name:string;version:string};spells:RoseSpell[]}

export const STARTER_SPELL_IDS:Readonly<Record<PlayerClass,readonly number[]>>={
  Warrior:[71],Scholar:[71,29],Gypsy:[71],Priest:[25,29],Mage:[71,3,244],Archtypical:[71],
};

export function validateSpellFixture(value:unknown):SpellFixture{
  if(!value||typeof value!=="object")throw new Error("spell fixture must be an object");
  const fixture=value as SpellFixture;
  if(fixture.contract?.name!=="mud2026.rose-spells"||fixture.contract.version!=="1.0.0")throw new Error("unsupported spell fixture contract");
  if(!Array.isArray(fixture.spells)||fixture.spells.some(spell=>!Number.isInteger(spell.id)||!spell.name||!Array.isArray(spell.effects)))throw new Error("invalid spell records");
  return fixture;
}

export function castingBonus(playerClass:PlayerClass,level:number):number{
  // Walk-number mapping is inferred from the recovered help ordering; formula is exact.
  return playerClass==="Priest"||playerClass==="Mage"?level*2:playerClass==="Scholar"?level:0;
}

export function spellSkill(spell:RoseSpell,proficiencies:Readonly<Record<number,number>>):number{
  const primary=(proficiencies[spell.sphere]??0)-spell.proficiency_requirement;
  if(!spell.secondary_sphere)return primary;
  return Math.floor(((proficiencies[spell.sphere]??0)+(proficiencies[spell.secondary_sphere]??0)-spell.proficiency_requirement-spell.secondary_requirement)/2);
}

export function castingThreshold(spell:RoseSpell,proficiencies:Readonly<Record<number,number>>,playerClass:PlayerClass,level:number):number{
  return Math.max(1,Math.min(100,85+castingBonus(playerClass,level)+spellSkill(spell,proficiencies)));
}

export function rollInclusive(min:number,max:number,random=Math.random):number{return min+Math.floor(random()*(max-min+1));}
export function rollDice(count:number,min:number,max:number,random=Math.random):number{let total=0;for(let i=0;i<count;i++)total+=rollInclusive(min,max,random);return total;}

export function spellMagnitude(spell:RoseSpell,casterLevel:number,random=Math.random):number{
  const effect=spell.effects[0];if(!effect)return 0;
  // Handler 1 is _HEALING_HITPOINTS: caster level rolls of the record's min/max.
  if(effect.handler===1)return rollDice(casterLevel,effect.dice_count,effect.roll_min,random);
  // Handler 0 is _CAUSE_DAMAGE: record dice count, then inclusive min/max per die.
  return rollDice(effect.dice_count,effect.roll_min,effect.roll_max,random);
}

export function recoverySeconds(spell:RoseSpell,aptitude:number):number{
  // _SPELL_RDELAY is confirmed bounded by base_recovery, but one helper is opaque.
  // This deterministic approximation preserves that invariant and is isolated here.
  return Math.max(.6,spell.base_recovery*(1-Math.min(40,Math.max(0,aptitude))*.01));
}

export function isHealingSpell(spell:RoseSpell):boolean{return spell.effects.some(effect=>effect.handler===1);}
export function isDamageSpell(spell:RoseSpell):boolean{return spell.effects.some(effect=>effect.handler===0);}
export function findSpell(spells:readonly RoseSpell[],raw:string):RoseSpell|undefined{const name=raw.trim().toLowerCase();return spells.find(spell=>spell.name.toLowerCase()===name||spell.abbreviation.toLowerCase()===name||String(spell.id)===name);}
