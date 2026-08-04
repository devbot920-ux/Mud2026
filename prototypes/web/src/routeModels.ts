export type RouteAnimation = "torch"|"speech"|"dust"|"scraps"|"glints"|"signs"|"arena"|"dais"|"altar";

export const TRAINING_ROUTE_MODELS: Readonly<Record<number,{path:string;animation:RouteAnimation;background:number;light:number}>>={
  3976:{path:"/models/generated/training_room_3976.glb",animation:"torch",background:0x07090b,light:0xffb45c},
  3977:{path:"/models/generated/linguistic_council_3977.glb",animation:"speech",background:0x100809,light:0xffc37a},
  3978:{path:"/models/generated/help_library_3978.glb",animation:"dust",background:0x0c0905,light:0xffa84a},
  3979:{path:"/models/generated/discarded_hall_3979.glb",animation:"scraps",background:0x090a08,light:0xd7b278},
  3980:{path:"/models/generated/wardroom_3980.glb",animation:"glints",background:0x090807,light:0xffc07a},
  3981:{path:"/models/generated/traders_pit_3981.glb",animation:"signs",background:0x100a05,light:0xffa34c},
  3982:{path:"/models/generated/practice_arena_3982.glb",animation:"arena",background:0x0d0706,light:0xff7655},
  3983:{path:"/models/generated/enlightenment_dais_3983.glb",animation:"dais",background:0x090711,light:0xb79cff},
  3984:{path:"/models/generated/advancement_altar_3984.glb",animation:"altar",background:0x100c05,light:0xffd36f},
};

export function trainingRouteModel(roomId:number){return TRAINING_ROUTE_MODELS[roomId];}
