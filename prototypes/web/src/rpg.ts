export type PlayerRace="Human"|"Elf"|"Dwarf"|"Gnome"|"Giant"|"Fairfolk";
export type PlayerClass="Warrior"|"Scholar"|"Gypsy"|"Priest"|"Mage"|"Archtypical";
export type EquipmentSlot="weapon"|"armor";
export type EquipmentId="training-knife"|"kobold-dagger"|"thug-jerkin"|"guard-hammer"|"slug-hide";
export type AttributeName="strength"|"wisdom"|"dexterity"|"constitution"|"intelligence"|"charisma"|"comeliness"|"perception";

export interface Equipment {id:EquipmentId;name:string;description:string;slot:EquipmentSlot;weight:number;damage?:number;armor?:number}
export type CharacterAttributes=Record<AttributeName,number>;
export interface CharacterStats {maxHealth:number;maxEndurance:number;maxMana:number;baseDamage:number;armor:number;carryCapacity:number;attackInterval:number}
export interface CharacterSkill {name:string;raw:number;adjusted:number;prime:AttributeName}
export interface Progression {level:number;experience:number;nextLevelExperience:number}
export interface Loadout {weapon?:EquipmentId;armor?:EquipmentId}

export const ATTRIBUTE_NAMES:readonly AttributeName[]=["strength","dexterity","constitution","wisdom","intelligence","perception","charisma","comeliness"];
export const RACES:readonly PlayerRace[]=["Human","Elf","Dwarf","Gnome","Giant","Fairfolk"];
export const CLASSES:readonly PlayerClass[]=["Warrior","Scholar","Gypsy","Priest","Mage","Archtypical"];
export const EQUIPMENT:Readonly<Record<EquipmentId,Equipment>>={
  "training-knife":{id:"training-knife",name:"training knife",description:"A balanced practice blade taken from the Pendelhaven training route.",slot:"weapon",weight:3,damage:5},
  "kobold-dagger":{id:"kobold-dagger",name:"kobold dagger",description:"A chipped but quick dagger recovered from a kobold.",slot:"weapon",weight:4,damage:8},
  "thug-jerkin":{id:"thug-jerkin",name:"kobold leather jerkin",description:"Layered leather that absorbs a modest amount of punishment.",slot:"armor",weight:12,armor:3},
  "guard-hammer":{id:"guard-hammer",name:"kobold guard hammer",description:"A heavy guard hammer with a punishing iron head.",slot:"weapon",weight:9,damage:12},
  "slug-hide":{id:"slug-hide",name:"hardened slug hide",description:"Cured hide from a giant slug, fashioned into flexible protection.",slot:"armor",weight:7,armor:2},
};

export const MOB_REWARDS:Readonly<Record<number,{experience:number;loot:EquipmentId}>>={
  4003:{experience:24,loot:"slug-hide"},129:{experience:32,loot:"kobold-dagger"},4004:{experience:55,loot:"thug-jerkin"},4006:{experience:85,loot:"guard-hammer"},
};

const RACE_MODIFIERS:Record<PlayerRace,Partial<CharacterAttributes>>={
  Human:{},Elf:{strength:-3,dexterity:6,constitution:-2,intelligence:1,comeliness:5,perception:5},
  Dwarf:{strength:3,dexterity:-4,constitution:7,wisdom:1},Gnome:{strength:-4,dexterity:5,constitution:3,intelligence:-1,comeliness:-2,perception:-3},
  Giant:{strength:8,dexterity:-4,constitution:6,charisma:-2,perception:-4},Fairfolk:{strength:-6,wisdom:-2,dexterity:8,constitution:-4,charisma:-2,comeliness:5},
};
const CLASS_MODIFIERS:Record<PlayerClass,Partial<CharacterAttributes>>={
  Warrior:{strength:5,constitution:4,intelligence:-2},Scholar:{strength:-2,wisdom:3,intelligence:6},Gypsy:{wisdom:3,dexterity:4,charisma:-2,perception:5},
  Priest:{wisdom:6,constitution:2,charisma:3},Mage:{strength:-4,wisdom:3,constitution:-3,intelligence:7},Archtypical:{},
};

export function characterAttributes(race:PlayerRace,playerClass:PlayerClass):CharacterAttributes{
  const result=Object.fromEntries(ATTRIBUTE_NAMES.map(name=>[name,35])) as CharacterAttributes;
  for(const modifiers of [RACE_MODIFIERS[race],CLASS_MODIFIERS[playerClass]])for(const [name,value] of Object.entries(modifiers))result[name as AttributeName]+=value!;
  return result;
}

export function characterStats(race:PlayerRace,playerClass:PlayerClass,level=1):CharacterStats{
  const a=characterAttributes(race,playerClass),classArmor=playerClass==="Warrior"?2:playerClass==="Scholar"?1:0;
  return {
    maxHealth:45+a.constitution*2+(level-1)*8,
    maxEndurance:55+a.constitution+a.dexterity,
    maxMana:10+Math.round((a.intelligence+a.constitution)*.8)+(level-1)*4,
    baseDamage:Math.max(2,Math.floor(a.strength/8))+Math.floor((level-1)/2),
    armor:classArmor,
    carryCapacity:a.strength*2+a.constitution,
    attackInterval:Math.max(.58,Math.min(1.35,1.15-(a.dexterity+a.constitution-70)*.008)),
  };
}

const SKILL_BASE:Record<PlayerClass,readonly number[]>={Warrior:[18,12,9,15,9,2],Scholar:[6,15,6,10,11,12],Gypsy:[10,10,12,6,16,6],Priest:[10,8,5,10,8,14],Mage:[4,6,3,8,9,17],Archtypical:[9,8,7,7,7,7]};
const SKILL_DEFINITIONS:readonly [string,AttributeName][]=[["Melee weaponry","strength"],["Empty hand combat","dexterity"],["Bowman","perception"],["Armor usage","constitution"],["Defensive dodge","dexterity"],["Magical defense","wisdom"]];
export function characterSkills(race:PlayerRace,playerClass:PlayerClass):CharacterSkill[]{const a=characterAttributes(race,playerClass);return SKILL_DEFINITIONS.map(([name,prime],index)=>{const raw=SKILL_BASE[playerClass][index];return {name,raw,prime,adjusted:Math.round(raw*(.75+a[prime]/100))};});}

export function experienceForNextLevel(level:number):number{return level*100;}
export function gainExperience(current:Progression,amount:number):{progression:Progression;levelsGained:number}{
  let level=current.level,experience=current.experience+Math.max(0,amount),levelsGained=0,next=experienceForNextLevel(level);
  while(experience>=next){experience-=next;level+=1;levelsGained+=1;next=experienceForNextLevel(level);}
  return {progression:{level,experience,nextLevelExperience:next},levelsGained};
}

export function attackDamage(stats:CharacterStats,weapon?:Equipment):number{return stats.baseDamage+(weapon?.damage??0);}
export function receivedDamage(rawDamage:number,stats:CharacterStats,armor?:Equipment):number{return Math.max(1,rawDamage-stats.armor-(armor?.armor??0));}
export function effectiveArmor(stats:CharacterStats,armor?:Equipment):number{return stats.armor+(armor?.armor??0);}
export function updateEndurance(current:number,max:number,seconds:number,running:boolean,moving:boolean):number{return Math.max(0,Math.min(max,current+seconds*(running?-18:moving?5:11)));}
export function inventoryWeight(items:Iterable<EquipmentId>):number{return [...items].reduce((total,id)=>total+EQUIPMENT[id].weight,0);}
export function equip(loadout:Loadout,item:Equipment):Loadout{return {...loadout,[item.slot]:item.id};}
export function unequip(loadout:Loadout,slot:EquipmentSlot):Loadout{const next={...loadout};delete next[slot];return next;}
export function rewardForMob(id:number){return MOB_REWARDS[id];}
export function findEquipment(raw:string):Equipment|undefined{const value=raw.trim().toLowerCase();return Object.values(EQUIPMENT).find(item=>item.name===value||item.id===value);}
