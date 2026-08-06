export const MIN_THIRD_PERSON_DISTANCE=2.4;
export const MAX_THIRD_PERSON_DISTANCE=9;

export function adjustThirdPersonDistance(current:number,wheelDeltaY:number):number{
  return Math.max(MIN_THIRD_PERSON_DISTANCE,Math.min(MAX_THIRD_PERSON_DISTANCE,current+wheelDeltaY*.006));
}
