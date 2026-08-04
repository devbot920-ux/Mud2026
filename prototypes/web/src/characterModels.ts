export type CharacterAnimation="slump"|"gossip"|"whisper"|"nod"|"lean"|"dummy"|"merchant"|"healer"|"trainer"|"slug"|"kobold"|"thug"|"guard";

export const TUTORIAL_CHARACTER_MODELS:Readonly<Record<number,{path:string;animation:CharacterAnimation}>>={
  3993:{path:"/models/generated/old_man_3993.glb",animation:"slump"},
  3994:{path:"/models/generated/lady_gossip_3994.glb",animation:"gossip"},
  3995:{path:"/models/generated/lady_whispers_3995.glb",animation:"whisper"},
  3996:{path:"/models/generated/lady_speech_3996.glb",animation:"nod"},
  3997:{path:"/models/generated/lazy_guard_3997.glb",animation:"lean"},
  3998:{path:"/models/generated/wooden_dummy_3998.glb",animation:"dummy"},
};

export const PENDELHAVEN_CHARACTER_MODELS:Readonly<Record<number,{path:string;animation:CharacterAnimation}>>={
  4175:{path:"/models/generated/big_ed_4175.glb",animation:"merchant"},
  4176:{path:"/models/generated/rhune_4176.glb",animation:"merchant"},
  4177:{path:"/models/generated/ooteeny_4177.glb",animation:"merchant"},
  4178:{path:"/models/generated/ezekiel_4178.glb",animation:"merchant"},
  4179:{path:"/models/generated/issac_4179.glb",animation:"merchant"},
  4180:{path:"/models/generated/davis_4180.glb",animation:"trainer"},
  4181:{path:"/models/generated/vivian_4181.glb",animation:"healer"},
  4182:{path:"/models/generated/oscar_4182.glb",animation:"trainer"},
  4003:{path:"/models/generated/giant_slug_4003.glb",animation:"slug"},
  129:{path:"/models/generated/kobold_129.glb",animation:"kobold"},
  4004:{path:"/models/generated/kobold_thug_4004.glb",animation:"thug"},
  4006:{path:"/models/generated/kobold_guard_4006.glb",animation:"guard"},
};

export function characterModel(entityId:number){return TUTORIAL_CHARACTER_MODELS[entityId]??PENDELHAVEN_CHARACTER_MODELS[entityId];}
