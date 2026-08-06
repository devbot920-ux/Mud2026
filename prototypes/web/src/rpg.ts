export type PlayerRace="Human"|"Elf"|"Dwarf"|"Kobold";
export type PlayerClass="Warrior"|"Rogue"|"Mage"|"Cleric";
export type EquipmentSlot="weapon"|"armor";
export type EquipmentId="training-knife"|"kobold-dagger"|"thug-jerkin"|"guard-hammer"|"slug-hide";

export interface Equipment {id:EquipmentId;name:string;slot:EquipmentSlot;damage?:number;armor?:number}
export interface CharacterStats {maxHealth:number;maxEndurance:number;baseDamage:number;armor:number}
export interface Progression {level:number;experience:number;nextLevelExperience:number}

export const RACES:readonly PlayerRace[]=["Human","Elf","Dwarf","Kobold"];
export const CLASSES:readonly PlayerClass[]=["Warrior","Rogue","Mage","Cleric"];
export const EQUIPMENT:Readonly<Record<EquipmentId,Equipment>>={
  "training-knife":{id:"training-knife",name:"training knife",slot:"weapon",damage:5},
  "kobold-dagger":{id:"kobold-dagger",name:"kobold dagger",slot:"weapon",damage:8},
  "thug-jerkin":{id:"thug-jerkin",name:"kobold leather jerkin",slot:"armor",armor:3},
  "guard-hammer":{id:"guard-hammer",name:"kobold guard hammer",slot:"weapon",damage:12},
  "slug-hide":{id:"slug-hide",name:"hardened slug hide",slot:"armor",armor:2},
};

export const MOB_REWARDS:Readonly<Record<number,{experience:number;loot:EquipmentId}>>={
  4003:{experience:24,loot:"slug-hide"},129:{experience:32,loot:"kobold-dagger"},4004:{experience:55,loot:"thug-jerkin"},4006:{experience:85,loot:"guard-hammer"},
};

export function characterStats(race:PlayerRace,playerClass:PlayerClass,level=1):CharacterStats{
  let maxHealth=100,maxEndurance=100,baseDamage=3,armor=0;
  if(race==="Elf"){maxHealth-=8;maxEndurance+=20;baseDamage+=1;}else if(race==="Dwarf"){maxHealth+=22;maxEndurance-=10;armor+=1;}else if(race==="Kobold"){maxHealth-=12;maxEndurance+=28;baseDamage+=2;}
  if(playerClass==="Warrior"){maxHealth+=30;baseDamage+=3;armor+=2;}else if(playerClass==="Rogue"){maxEndurance+=30;baseDamage+=2;}else if(playerClass==="Mage"){maxHealth-=12;baseDamage+=5;}else if(playerClass==="Cleric"){maxHealth+=15;baseDamage+=2;armor+=1;}
  maxHealth+=(level-1)*8;baseDamage+=Math.floor((level-1)/2);
  return {maxHealth,maxEndurance,baseDamage,armor};
}

export function experienceForNextLevel(level:number):number{return level*100;}
export function gainExperience(current:Progression,amount:number):{progression:Progression;levelsGained:number}{
  let level=current.level,experience=current.experience+Math.max(0,amount),levelsGained=0,next=experienceForNextLevel(level);
  while(experience>=next){experience-=next;level+=1;levelsGained+=1;next=experienceForNextLevel(level);}
  return {progression:{level,experience,nextLevelExperience:next},levelsGained};
}

export function attackDamage(stats:CharacterStats,weapon?:Equipment):number{return stats.baseDamage+(weapon?.damage??0);}
export function receivedDamage(rawDamage:number,stats:CharacterStats,armor?:Equipment):number{return Math.max(1,rawDamage-stats.armor-(armor?.armor??0));}
export function updateEndurance(current:number,max:number,seconds:number,running:boolean,moving:boolean):number{return Math.max(0,Math.min(max,current+seconds*(running?-18:moving?5:11)));}
export function rewardForMob(id:number){return MOB_REWARDS[id];}
export function findEquipment(raw:string):Equipment|undefined{const value=raw.trim().toLowerCase();return Object.values(EQUIPMENT).find(item=>item.name===value||item.id===value);}
