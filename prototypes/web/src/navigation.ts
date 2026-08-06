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

interface Rect {minX:number;maxX:number;minZ:number;maxZ:number}
const OBSTACLES:Readonly<Record<number,readonly Rect[]>>={
  3984:[{minX:-2.6,maxX:2.6,minZ:-3.0,maxZ:.7}],
  4165:[{minX:-2.8,maxX:2.8,minZ:-2.3,maxZ:2.3}],
  4166:[{minX:-5.5,maxX:5.5,minZ:-5.8,maxZ:-3.5}],
  4167:[{minX:-5.8,maxX:5.8,minZ:-6.2,maxZ:-4.2}],
  4168:[{minX:3.5,maxX:6.8,minZ:-4.3,maxZ:-1.2}],
  4169:[{minX:-2.3,maxX:2.3,minZ:-2.8,maxZ:1.2}],
  4171:[{minX:-6,maxX:-1.25,minZ:-5.8,maxZ:-3.8},{minX:1.25,maxX:6,minZ:-5.8,maxZ:-3.8}],
  4172:[{minX:-1.8,maxX:1.8,minZ:-1.8,maxZ:1.8}],
  4173:[{minX:-6.4,maxX:6.4,minZ:-6.3,maxZ:-4.2}],
};

export function constrainModeledMovement(roomId:number,current:{x:number;z:number},proposed:{x:number;z:number}){
  const candidate={x:Math.max(-8.5,Math.min(8.5,proposed.x)),z:Math.max(-8.5,Math.min(8.5,proposed.z))};
  const blocked=(OBSTACLES[roomId]??[]).some(rect=>candidate.x>rect.minX&&candidate.x<rect.maxX&&candidate.z>rect.minZ&&candidate.z<rect.maxZ);
  return blocked?{x:current.x,z:current.z}:candidate;
}

export function modeledFloorHeight(roomId:number,position:{x:number;z:number}):number{
  if(roomId!==3983||Math.abs(position.x+position.z)>2.25)return 0;
  const along=(position.x-position.z)/Math.SQRT2;
  return Math.max(0,Math.min(1.12,(along-.25)*.22));
}
