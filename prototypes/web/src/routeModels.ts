export type RouteAnimation = "torch"|"speech"|"dust"|"scraps"|"glints"|"signs"|"arena"|"dais"|"altar"|"square"|"armor"|"forge"|"summoning"|"healing"|"guild"|"bank"|"store"|"tavern";

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
  4165:{path:"/models/generated/pendelhaven_square_4165.glb",animation:"square",background:0x18232a,light:0xffd29a},
  4166:{path:"/models/generated/armor_shop_4166.glb",animation:"armor",background:0x120d09,light:0xffc37d},
  4167:{path:"/models/generated/weapon_shop_4167.glb",animation:"forge",background:0x130907,light:0xff7b45},
  4168:{path:"/models/generated/pendelhaven_arena_4168.glb",animation:"summoning",background:0x10070b,light:0xff7058},
  4169:{path:"/models/generated/pendelhaven_hospice_4169.glb",animation:"healing",background:0x11101b,light:0xd9c7ff},
  4170:{path:"/models/generated/pendelhaven_guild_4170.glb",animation:"guild",background:0x100b08,light:0xffad69},
  4171:{path:"/models/generated/pendelhaven_bank_4171.glb",animation:"bank",background:0x0d1012,light:0xffda8c},
  4172:{path:"/models/generated/general_store_4172.glb",animation:"store",background:0x15100a,light:0xffc477},
  4173:{path:"/models/generated/pendelhaven_tavern_4173.glb",animation:"tavern",background:0x100806,light:0xff8d50},
};

export function trainingRouteModel(roomId:number){return TRAINING_ROUTE_MODELS[roomId];}
