export type CharacterAnimation="slump"|"gossip"|"whisper"|"nod"|"lean"|"dummy";

export const TUTORIAL_CHARACTER_MODELS:Readonly<Record<number,{path:string;animation:CharacterAnimation}>>={
  3993:{path:"/models/generated/old_man_3993.glb",animation:"slump"},
  3994:{path:"/models/generated/lady_gossip_3994.glb",animation:"gossip"},
  3995:{path:"/models/generated/lady_whispers_3995.glb",animation:"whisper"},
  3996:{path:"/models/generated/lady_speech_3996.glb",animation:"nod"},
  3997:{path:"/models/generated/lazy_guard_3997.glb",animation:"lean"},
  3998:{path:"/models/generated/wooden_dummy_3998.glb",animation:"dummy"},
};

export function tutorialCharacterModel(entityId:number){return TUTORIAL_CHARACTER_MODELS[entityId];}
