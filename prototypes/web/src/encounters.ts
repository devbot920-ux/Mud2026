export const WORLD_RESPAWN_DELAY_MS=120_000;

export function defeatKey(roomId:number,mobId:number):string{return `${roomId}:${mobId}`;}
export function defeatExpiresAt(now:number):number{return now+WORLD_RESPAWN_DELAY_MS;}
export function defeatStillActive(until:number|undefined,now:number):boolean{return until!==undefined&&now<until;}
