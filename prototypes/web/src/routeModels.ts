export type RouteAnimation = "torch"|"speech"|"dust"|"scraps"|"glints"|"signs"|"arena";

export const TRAINING_ROUTE_MODELS: Readonly<Record<number,{path:string;animation:RouteAnimation}>>={
  3976:{path:"/models/generated/training_room_3976.glb",animation:"torch"},
  3977:{path:"/models/generated/linguistic_council_3977.glb",animation:"speech"},
  3978:{path:"/models/generated/help_library_3978.glb",animation:"dust"},
  3979:{path:"/models/generated/discarded_hall_3979.glb",animation:"scraps"},
  3980:{path:"/models/generated/wardroom_3980.glb",animation:"glints"},
  3981:{path:"/models/generated/traders_pit_3981.glb",animation:"signs"},
  3982:{path:"/models/generated/practice_arena_3982.glb",animation:"arena"},
};

export function trainingRouteModel(roomId:number){return TRAINING_ROUTE_MODELS[roomId];}
