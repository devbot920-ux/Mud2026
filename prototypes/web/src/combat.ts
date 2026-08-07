export interface HostileStats {name:string;maxHealth:number;damage:number;attackInterval:number;armor:number;sourceBehavior:number}

export const ARENA_ROSTER=[4003,129,4004,4006] as const;
export const HOSTILE_STATS:Readonly<Record<number,HostileStats>>={
  4003:{name:"giant slug",maxHealth:24,damage:3,attackInterval:1.65,armor:0,sourceBehavior:1},
  129:{name:"kobold",maxHealth:32,damage:4,attackInterval:1.35,armor:1,sourceBehavior:1},
  4004:{name:"kobold thug",maxHealth:44,damage:6,attackInterval:1.2,armor:2,sourceBehavior:1},
  4006:{name:"kobold guard",maxHealth:60,damage:8,attackInterval:1.05,armor:4,sourceBehavior:1},
};

export function arenaOpponent(round:number):number{return ARENA_ROSTER[((round%ARENA_ROSTER.length)+ARENA_ROSTER.length)%ARENA_ROSTER.length];}
export function hostileStats(id:number):HostileStats|undefined{return HOSTILE_STATS[id];}
export function sourceBehavior(code:number):"aggressive"|"criminals-only"|"passive"{return code===1?"aggressive":code===2?"criminals-only":"passive";}
export function shouldAutoAggro(id:number):boolean{return sourceBehavior(HOSTILE_STATS[id]?.sourceBehavior??0)==="aggressive";}
export function playerDamage(hasKnife:boolean):number{return hasKnife?8:3;}
export function matchesHostileName(id:number,target:string):boolean{
  const stats=hostileStats(id);if(!stats)return false;
  const value=target.trim().toLowerCase();return value===stats.name||value===stats.name.replace(/^giant /,"")||value==="mob"||value==="opponent";
}
