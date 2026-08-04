export interface EntrySpawn {x:number;z:number;yaw:number;incomingDirection:string}

const OPPOSITE:Readonly<Record<string,string>>={N:"S",NE:"SW",E:"W",SE:"NW",S:"N",SW:"NE",W:"E",NW:"SE",U:"D",D:"U"};
const ENTRY_POINTS:Readonly<Record<string,{x:number;z:number}>>={
  N:{x:0,z:-6.65},NE:{x:4.7,z:-4.7},E:{x:6.65,z:0},SE:{x:4.7,z:4.7},S:{x:0,z:6.65},SW:{x:-4.7,z:4.7},W:{x:-6.65,z:0},NW:{x:-4.7,z:-4.7},
  U:{x:2.7,z:-2.7},D:{x:-2.7,z:2.7},
};

export function entrySpawnAfterTravel(outgoingDirection:string,actualArrivalDirection?:string):EntrySpawn|undefined{
  const incomingDirection=actualArrivalDirection??OPPOSITE[outgoingDirection];const point=ENTRY_POINTS[incomingDirection];
  if(!point)return undefined;
  return {x:point.x,z:point.z,yaw:Math.atan2(point.x,point.z),incomingDirection};
}

export function horizontalTriggerReached(player:{x:number;z:number},trigger:{x:number;z:number},radius=1.05){return Math.hypot(trigger.x-player.x,trigger.z-player.z)<radius;}
