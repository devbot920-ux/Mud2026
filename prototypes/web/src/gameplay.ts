import type { Point2 } from "./room3976";

export interface PositionedEntity extends Point2 { id: number }
export type GameplayCommand = "get-knife" | "attack-dummy" | "stop-combat" | "inventory";

export function findFacingEntity<T extends PositionedEntity>(position: Point2, forward: Point2, entities: readonly T[], maxDistance = 3.25): T | undefined {
  const forwardLength=Math.hypot(forward.x,forward.z);
  if(forwardLength<0.001)return undefined;
  let best: {entity:T;distance:number}|undefined;
  for(const entity of entities){
    const dx=entity.x-position.x,dz=entity.z-position.z,distance=Math.hypot(dx,dz);
    if(distance<0.001||distance>maxDistance)continue;
    const facing=(dx*forward.x+dz*forward.z)/(distance*forwardLength);
    if(facing<0.55)continue;
    if(!best||distance<best.distance)best={entity,distance};
  }
  return best?.entity;
}

export function gameplayCommand(raw:string): GameplayCommand|undefined {
  const command=raw.trim().toLowerCase().replace(/\s+/g," ");
  if(/^(get|take|pick up) (a |the )?knife$/.test(command))return "get-knife";
  if(/^(attack|a|fight|hit) (the )?(wooden )?dummy$/.test(command))return "attack-dummy";
  if(command==="stop"||command==="stop fighting")return "stop-combat";
  if(command==="inventory"||command==="inv"||command==="i")return "inventory";
  return undefined;
}

export function practiceDamage(hasKnife:boolean):number{return hasKnife?5:2;}
