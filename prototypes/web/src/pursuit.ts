export function distance2d(a:{x:number;z:number},b:{x:number;z:number}):number{return Math.hypot(a.x-b.x,a.z-b.z);}
export function canMobFollow(edge:{hidden?:boolean;to_room:number},primaryRooms:readonly number[]):boolean{return !edge.hidden&&primaryRooms.includes(edge.to_room);}
export function exitBlocked(mob:{x:number;z:number}|undefined,exit:{x:number;z:number},engaged:boolean,sprinting:boolean):boolean{return !!mob&&engaged&&!sprinting&&distance2d(mob,exit)<=3.1;}
export function chaseStep(from:{x:number;z:number},to:{x:number;z:number},speed:number,seconds:number):{x:number;z:number}{const distance=distance2d(from,to);if(distance===0)return {...from};const step=Math.min(distance,speed*seconds);return {x:from.x+(to.x-from.x)/distance*step,z:from.z+(to.z-from.z)/distance*step};}
