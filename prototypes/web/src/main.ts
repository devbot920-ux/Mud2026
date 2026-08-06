import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import {EffectComposer} from "three/addons/postprocessing/EffectComposer.js";
import {RenderPass} from "three/addons/postprocessing/RenderPass.js";
import {UnrealBloomPass} from "three/addons/postprocessing/UnrealBloomPass.js";
import {OutputPass} from "three/addons/postprocessing/OutputPass.js";
import "./style.css";
import { commandDirection, edgesFrom, field, travel, validateWorld, type Edge, type Entity, type Room, type World } from "./model";
import { INITIAL_ROOM_ID, constrainInitialRoomMovement, findInitialRoomTarget, initialRoomCommand, type InitialRoomAction } from "./room3976";
import { attackTargetName, findFacingEntity, gameplayCommand } from "./gameplay";
import { trainingRouteModel, type RouteAnimation } from "./routeModels";
import { characterModel, type CharacterAnimation } from "./characterModels";
import { constrainModeledMovement, entrySpawnAfterTravel, horizontalTriggerReached, modeledFloorHeight } from "./navigation";
import { arenaOpponent, hostileStats, matchesHostileName } from "./combat";
import {ATTRIBUTE_NAMES,CLASSES,EQUIPMENT,RACES,attackDamage,characterAttributes,characterSkills,characterStats,effectiveArmor,findEquipment,gainExperience,inventoryWeight,receivedDamage,resolveMeleeAttack,rewardForMob,updateEndurance,type EquipmentId,type EquipmentSlot,type PlayerClass,type PlayerRace} from "./rpg";
import {animatePlayerAvatar,createPlayerAvatar,setAvatarEquipment,type PlayerAvatar} from "./playerAvatar";
import {adjustThirdPersonDistance} from "./cameraControl";
import {STARTER_SPELL_IDS,castingThreshold,findSpell,isDamageSpell,isHealingSpell,recoverySeconds,spellMagnitude,validateSpellFixture,type RoseSpell,type SpellFixture} from "./spells";
import {canMobFollow,chaseStep,distance2d,exitBlocked} from "./pursuit";

const canvas = document.querySelector<HTMLCanvasElement>("#world")!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference:"high-performance" });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.12;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x07090b); scene.fog = new THREE.Fog(0x07090b, 12, 29);
const camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, .05, 80); camera.rotation.order = "YXZ";
const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));const bloomPass=new UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight),.24,.35,.84);composer.addPass(bloomPass);composer.addPass(new OutputPass());
const chamber = new THREE.Group(); scene.add(chamber);
const modelLoader = new GLTFLoader();
const textureLoader=new THREE.TextureLoader();
function surfaceTexture(path:string){const texture=textureLoader.load(path);texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.repeat.set(2.4,2.4);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=renderer.capabilities.getMaxAnisotropy();return texture;}
const stoneTexture=surfaceTexture("/textures/generated/pendelhaven-stone-v1.png"),woodTexture=surfaceTexture("/textures/generated/pendelhaven-oak-v1.png");
const loadedModels = new Set<string>();
const skyLight=new THREE.HemisphereLight(0x8ba7b5, 0x251a0e, 1.6);scene.add(skyLight);
const torch = new THREE.PointLight(0xffb45c, 40, 24); torch.position.set(0, 3.2, 0); torch.castShadow = true; scene.add(torch);
const keyLight=new THREE.DirectionalLight(0xffe1b0,2.2);keyLight.position.set(-7,12,6);keyLight.castShadow=true;keyLight.shadow.mapSize.set(2048,2048);keyLight.shadow.camera.left=-12;keyLight.shadow.camera.right=12;keyLight.shadow.camera.top=12;keyLight.shadow.camera.bottom=-12;scene.add(keyLight);

let world: World;let spellFixture:SpellFixture; let currentRoomId = INITIAL_ROOM_ID; let showHidden = false; let developerVisible = false;
let yaw = 0, pitch = 0, roomGeneration = 0; const keys = new Set<string>(); const exitTriggers: { edge: Edge; position: THREE.Vector3 }[] = [];
const title = document.querySelector<HTMLElement>("#title")!; const description = document.querySelector<HTMLElement>("#description")!;
const exitsElement = document.querySelector<HTMLElement>("#exits")!; const developer = document.querySelector<HTMLElement>("#developer")!;
const interactionPrompt = document.querySelector<HTMLElement>("#interaction-prompt")!; const interactionPanel = document.querySelector<HTMLElement>("#interaction-panel")!;
const interactionTitle = document.querySelector<HTMLElement>("#interaction-title")!; const interactionText = document.querySelector<HTMLElement>("#interaction-text")!;
const proximityActions=document.querySelector<HTMLElement>("#proximity-actions")!,proximityButtons=document.querySelector<HTMLElement>("#proximity-buttons")!;
const tutorial = document.querySelector<HTMLElement>("#tutorial")!; const tutorialProgress = new Set<"look"|"old-man"|"parchment"|"west">();
const playerStatus = document.querySelector<HTMLElement>("#player-status")!;
const gamePanel=document.querySelector<HTMLElement>("#game-panel")!,gamePanelTitle=document.querySelector<HTMLElement>("#game-panel-title")!,gamePanelContent=document.querySelector<HTMLElement>("#game-panel-content")!,gamePanelClose=document.querySelector<HTMLButtonElement>("#game-panel-close")!,controlModeButton=document.querySelector<HTMLButtonElement>("#control-mode")!,commandForm=document.querySelector<HTMLFormElement>("#command-form")!,commandInput=document.querySelector<HTMLInputElement>("#command")!;
const characterCreation=document.querySelector<HTMLElement>("#character-creation")!,characterForm=document.querySelector<HTMLFormElement>("#character-form")!,characterNameInput=document.querySelector<HTMLInputElement>("#character-name")!,characterRaceSelect=document.querySelector<HTMLSelectElement>("#character-race")!,characterClassSelect=document.querySelector<HTMLSelectElement>("#character-class")!,characterPreview=document.querySelector<HTMLElement>("#character-preview")!;
interface RoomInteraction { id:number; entity: Entity; kind: "npc"|"item"; position: THREE.Vector3; count: number; x:number; z:number }
const roomInteractions: RoomInteraction[]=[]; const inventory=new Set<number>();
let activeEntityId: number|undefined, activeNearbyEntityId:number|undefined; let interactionPinned=false;
let combatTargetId: number|undefined, dummyHealth=30, combatTargetHealth=0, combatClock=0, enemyCombatClock=0;
let playerHealth=100,playerEndurance=100,playerMana=100,arenaRound=-1,arenaOpponentId:number|undefined,victories=0;
let characterCreated=false,playerName="Adventurer",playerRace:PlayerRace="Human",playerClass:PlayerClass="Warrior",progression={level:1,experience:0,nextLevelExperience:100};
let equippedWeapon:EquipmentId|undefined,equippedArmor:EquipmentId|undefined;const ownedEquipment=new Set<EquipmentId>();const defeatedMobs=new Map<string,number>();
let thirdPerson=true,thirdPersonDistance=5.8,vHeld=false,vZoomed=false,playerAvatar:PlayerAvatar|undefined;const playerPosition=new THREE.Vector3(0,0,0);
let openPanel:"inventory"|"character"|"spells"|undefined,inputMode:"mouse"|"command"="mouse";
let spellRecovery=0,pursuingMobId:number|undefined,pursuingMobHealth=0,pursuitRoomId:number|undefined,proximitySignature="";
interface AmbientMotion {object:THREE.Object3D;kind:RouteAnimation;phase:number;baseY:number}
const ambientMotions:AmbientMotion[]=[]; let dummyVisual:THREE.Group|undefined;
interface CharacterMotion {id:number;root:THREE.Group;head?:THREE.Object3D;kind:CharacterAnimation;baseY:number;baseRotationY:number}
const characterMotions:CharacterMotion[]=[];let activeHostileVisual:THREE.Group|undefined;
const floatingCombatTexts:{sprite:THREE.Sprite;life:number}[]=[];
const HOSTILE_IDS=new Set([129,4003,4004,4006]);

const ENTITY_POSITIONS:Readonly<Record<number,{x:number;y:number;z:number}>>={
  3993:{x:2.7,y:.42,z:-7.15},3985:{x:-2.6,y:2.05,z:-8.55},3991:{x:2,y:.35,z:-2},3992:{x:0,y:1,z:-1.2},
  4175:{x:4.7,y:.42,z:-3.5},4176:{x:-3.5,y:.42,z:-3.0},4177:{x:3.4,y:.42,z:-3.0},4178:{x:4.4,y:.42,z:-1.8},
  4179:{x:4.2,y:.42,z:-2.8},4180:{x:3.8,y:.42,z:-2.8},4181:{x:4.5,y:.42,z:2.2},4182:{x:4.8,y:.42,z:1.8},
  129:{x:0,y:.42,z:0},4003:{x:0,y:.25,z:0},4004:{x:0,y:.42,z:0},4006:{x:0,y:.42,z:0},
};

const positions: Record<string, THREE.Vector3> = {
  N: new THREE.Vector3(0,0,-8), NE:new THREE.Vector3(5.65,0,-5.65), E:new THREE.Vector3(8,0,0), SE:new THREE.Vector3(5.65,0,5.65),
  S:new THREE.Vector3(0,0,8), SW:new THREE.Vector3(-5.65,0,5.65), W:new THREE.Vector3(-8,0,0), NW:new THREE.Vector3(-5.65,0,-5.65), U:new THREE.Vector3(4,1.5,-4), D:new THREE.Vector3(-4,-.4,4),
};

function material(color: number, roughness=.8) { return new THREE.MeshStandardMaterial({ color, roughness }); }
function addBox(size: THREE.Vector3, at: THREE.Vector3, color: number) { const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size.toArray()), material(color)); mesh.position.copy(at); mesh.receiveShadow = mesh.castShadow = true; chamber.add(mesh); return mesh; }

async function addModel(path: string, generation: number, configure?: (model: THREE.Group) => void) {
  try {
    const gltf = await modelLoader.loadAsync(path);
    if (generation !== roomGeneration) return;
    gltf.scene.traverse(object => { if (object instanceof THREE.Mesh){object.castShadow = object.receiveShadow = true;const originals=Array.isArray(object.material)?object.material:[object.material];const enhanced=originals.map(original=>{if(!(original instanceof THREE.MeshStandardMaterial))return original;const next=original.clone(),name=`${next.name} ${object.name}`.toLowerCase();if(/stone|wall|floor|marble|altar|dais|plaza|hearth|paving|masonry/.test(name)){next.map=stoneTexture;next.color.lerp(new THREE.Color(0xffffff),.58);next.roughness=Math.max(next.roughness,.72);}else if(/wood|oak|timber|counter|stage|shelf|table|rack|bar|desk|bench/.test(name)){next.map=woodTexture;next.color.lerp(new THREE.Color(0xffffff),.62);next.roughness=Math.max(next.roughness,.62);}next.needsUpdate=true;return next;});object.material=Array.isArray(object.material)?enhanced:enhanced[0];} });
    configure?.(gltf.scene);
    chamber.add(gltf.scene);
    loadedModels.add(path);
  } catch (error) {
    console.warn(`Unable to load ${path}; keeping the procedural marker.`, error);
  }
}

function addKnifeModel(position:THREE.Vector3){const group=new THREE.Group();const blade=new THREE.Mesh(new THREE.BoxGeometry(.12,.06,.85),material(0xc7ced0,.3));blade.position.z=-.24;const handle=new THREE.Mesh(new THREE.BoxGeometry(.2,.12,.38),material(0x5b351c,.8));handle.position.z=.37;group.add(blade,handle);group.position.copy(position).setY(.3);group.rotation.y=.55;group.traverse(o=>{if(o instanceof THREE.Mesh)o.castShadow=true;});chamber.add(group);}

function trackAmbient(object:THREE.Object3D,kind:RouteAnimation,phase=0){chamber.add(object);ambientMotions.push({object,kind,phase,baseY:object.position.y});}
function addRoomAnimation(kind:RouteAnimation){
  if(kind==="speech")for(const [index,x] of [-3,0,3].entries()){const orb=new THREE.Mesh(new THREE.TorusGeometry(.24,.055,8,20),new THREE.MeshBasicMaterial({color:0xf0c66d,transparent:true,opacity:.72}));orb.position.set(x,2.7,-2.5);orb.rotation.x=Math.PI/2;trackAmbient(orb,kind,index*1.7);}
  else if(kind==="dust")for(let i=0;i<16;i++){const mote=new THREE.Mesh(new THREE.SphereGeometry(.025,5,4),new THREE.MeshBasicMaterial({color:0xe4d7aa,transparent:true,opacity:.42}));mote.position.set(((i*37)%100)/7-7, .4+((i*29)%40)/10,((i*53)%100)/7-7);trackAmbient(mote,kind,i*.61);}
  else if(kind==="scraps")for(let i=0;i<7;i++){const scrap=new THREE.Mesh(new THREE.PlaneGeometry(.44,.26),new THREE.MeshBasicMaterial({color:0xb69a66,side:THREE.DoubleSide}));scrap.position.set(-5+i*1.65,.22,-2+((i*17)%5));trackAmbient(scrap,kind,i*.77);}
  else if(kind==="glints")for(let i=0;i<4;i++){const glint=new THREE.Mesh(new THREE.SphereGeometry(.07,7,5),new THREE.MeshBasicMaterial({color:0xeafcff}));glint.position.set(6.85,1.75,-2.4+i*1.6);trackAmbient(glint,kind,i*.9);}
  else if(kind==="signs")for(const [index,x] of [-4.2,4.2].entries()){const pivot=new THREE.Group();pivot.position.set(x,3.0,-.05);const sign=new THREE.Mesh(new THREE.BoxGeometry(1.7,.72,.08),new THREE.MeshStandardMaterial({color:index?0x315889:0x8b3126,roughness:.8}));sign.position.y=-.42;pivot.add(sign);trackAmbient(pivot,kind,index*1.3);}
  else if(kind==="arena"){const ring=new THREE.Mesh(new THREE.TorusGeometry(3.8,.045,7,48),new THREE.MeshBasicMaterial({color:0xd65a42,transparent:true,opacity:.45}));ring.rotation.x=Math.PI/2;ring.position.y=.04;trackAmbient(ring,kind,0);}
  else if(kind==="dais")for(let i=0;i<7;i++){const glyph=new THREE.Mesh(new THREE.BoxGeometry(.3,.035,.18),new THREE.MeshBasicMaterial({color:0xd8a63f}));glyph.position.set(.45+i*.52,.18+i*.13,-.45-i*.52);glyph.rotation.y=-Math.PI/4;trackAmbient(glyph,kind,i*.55);}
  else if(kind==="altar"){const glow=new THREE.Mesh(new THREE.SphereGeometry(.22,12,8),new THREE.MeshBasicMaterial({color:0xffd875,transparent:true,opacity:.72}));glow.position.set(0,2.35,-1.2);trackAmbient(glow,kind,0);}
  else if(kind==="square")for(const [i,x] of [-2.2,2.2].entries()){const banner=new THREE.Mesh(new THREE.PlaneGeometry(1.1,2.4),new THREE.MeshStandardMaterial({color:i?0x315b78:0x8b3b35,side:THREE.DoubleSide}));banner.position.set(x,3.3,0);trackAmbient(banner,kind,i*1.2);}
  else if(kind==="forge")for(let i=0;i<12;i++){const ember=new THREE.Mesh(new THREE.SphereGeometry(.035,5,4),new THREE.MeshBasicMaterial({color:0xff6b26}));ember.position.set(-5.2,.7+i*.08,-5.5);trackAmbient(ember,kind,i*.4);}
  else if(kind==="summoning"){const ring=new THREE.Mesh(new THREE.TorusGeometry(3,.07,8,64),new THREE.MeshBasicMaterial({color:0xe43b35,transparent:true,opacity:.65}));ring.rotation.x=Math.PI/2;ring.position.y=.07;trackAmbient(ring,kind,0);}
  else if(kind==="healing")for(let i=0;i<8;i++){const mote=new THREE.Mesh(new THREE.SphereGeometry(.06,7,5),new THREE.MeshBasicMaterial({color:0xc9b4ff,transparent:true,opacity:.65}));mote.position.set(Math.cos(i*.8)*2,1+i*.2,Math.sin(i*.8)*2-.8);trackAmbient(mote,kind,i*.7);}
  else if(kind==="guild"){const pulse=new THREE.Mesh(new THREE.TorusGeometry(2.6,.045,7,48),new THREE.MeshBasicMaterial({color:0xffa75c,transparent:true,opacity:.4}));pulse.rotation.x=Math.PI/2;pulse.position.y=.05;trackAmbient(pulse,kind,0);}
  else if(kind==="bank"||kind==="armor")for(let i=0;i<6;i++){const glint=new THREE.Mesh(new THREE.SphereGeometry(.045,6,4),new THREE.MeshBasicMaterial({color:0xffdd8a}));glint.position.set(-2.5+i,1.45,-4);trackAmbient(glint,kind,i*.65);}
  else if(kind==="store"||kind==="tavern")for(let i=0;i<9;i++){const mote=new THREE.Mesh(new THREE.SphereGeometry(.05,6,4),new THREE.MeshBasicMaterial({color:kind==="tavern"?0x806a58:0xd6bc81,transparent:true,opacity:.28}));mote.position.set(-4+i,1+(i%4),-2+(i%3));trackAmbient(mote,kind,i*.5);}
}
function animateRoom(now:number){const t=now/1000;torch.intensity=currentRoomId===INITIAL_ROOM_ID?36+Math.sin(t*9)*4+Math.sin(t*17)*2:25;for(const motion of ambientMotions){const o=motion.object,p=motion.phase;if(motion.kind==="speech"){o.position.y=motion.baseY+Math.sin(t*2.2+p)*.18;o.rotation.z=t*.45+p;}else if(motion.kind==="dust"){o.position.y=.25+((motion.baseY+t*.18+p)%4.1);o.position.x+=Math.sin(t*.5+p)*.0008;}else if(motion.kind==="scraps"){o.position.y=motion.baseY+.08+Math.sin(t*1.5+p)*.09;o.rotation.x=t*.35+p;o.rotation.y=t*.22+p;}else if(motion.kind==="glints"){const s=.35+Math.max(0,Math.sin(t*3+p))*1.2;o.scale.setScalar(s);}else if(motion.kind==="signs")o.rotation.z=Math.sin(t*.85+p)*.075;else if(motion.kind==="arena"){const s=1+Math.sin(t*1.7)*.018;o.scale.setScalar(s);}else if(motion.kind==="dais"){const s=.6+Math.max(0,Math.sin(t*2+p))*.9;o.scale.setScalar(s);}else if(motion.kind==="altar"){o.position.y=motion.baseY+Math.sin(t*1.4)*.18;const s=.8+Math.sin(t*2.1)*.14;o.scale.setScalar(s);}}for(const motion of characterMotions){motion.root.position.y=motion.baseY;if(motion.kind==="slump")motion.root.rotation.z=-.07+Math.sin(t*.7)*.018;else if(motion.kind==="gossip")motion.root.rotation.y=motion.baseRotationY+Math.sin(t*.9)*.28;else if(motion.kind==="whisper")motion.root.position.y=motion.baseY+Math.sin(t*1.2)*.025;else if(motion.kind==="nod"&&motion.head)motion.head.rotation.x=Math.sin(t*2.25)*.16;else if(motion.kind==="lean")motion.root.rotation.z=.08+Math.sin(t*.55)*.018;}if(dummyVisual)dummyVisual.rotation.z=combatTargetId===3998?Math.sin(t*13)*.045:THREE.MathUtils.lerp(dummyVisual.rotation.z,0,.08);}

function animateCentralMotions(now:number){const t=now/1000;for(const motion of ambientMotions){const o=motion.object,p=motion.phase;if(motion.kind==="square")o.rotation.y=Math.sin(t*.8+p)*.09;else if(motion.kind==="forge"){o.position.y=motion.baseY+((t*.7+p)%1.8);o.scale.setScalar(.5+Math.sin(t*4+p)*.25);}else if(motion.kind==="summoning"||motion.kind==="guild"){const s=1+Math.sin(t*2+p)*.035;o.scale.setScalar(s);o.rotation.z=t*.08;}else if(motion.kind==="healing"){o.position.y=motion.baseY+Math.sin(t*1.4+p)*.35;o.rotation.y=t*.3+p;}else if(motion.kind==="bank"||motion.kind==="armor"){const s=.4+Math.max(0,Math.sin(t*3+p));o.scale.setScalar(s);}else if(motion.kind==="store"||motion.kind==="tavern")o.position.y=motion.baseY+((t*.12+p)%2.4);}for(const motion of characterMotions){if(motion.kind==="merchant")motion.root.rotation.y=motion.baseRotationY+Math.sin(t*.55+motion.id)*.08;else if(motion.kind==="healer")motion.root.position.y=motion.baseY+Math.sin(t*1.4)*.035;else if(motion.kind==="trainer")motion.root.rotation.y=motion.baseRotationY+Math.sin(t*.9)*.14;else if(motion.kind==="slug")motion.root.scale.z=1+Math.sin(t*3)*.06;else if(motion.kind==="kobold"||motion.kind==="thug"||motion.kind==="guard")motion.root.rotation.z=(combatTargetId===motion.id?Math.sin(t*9)*.04:Math.sin(t*1.8+motion.id)*.015);}if(activeHostileVisual&&combatTargetId&&HOSTILE_IDS.has(combatTargetId))activeHostileVisual.position.z=Math.sin(t*5)*.04;}

function marker(entity: Entity, kind: "npc"|"item", index: number, generation: number, count: number) {
  const color = kind === "npc" ? 0xa94d3c : 0xc3a44d; const radius = kind === "npc" ? .42 : .25;
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 18, 12), material(color,.55));
  const angle = index * 2.2; const defaultPosition = new THREE.Vector3(Math.cos(angle) * 2.3, radius, Math.sin(angle) * 2.3);
  const configured=HOSTILE_IDS.has(entity.id)&&currentRoomId!==4168?undefined:ENTITY_POSITIONS[entity.id];const knownPosition=configured?new THREE.Vector3(configured.x,configured.y,configured.z):defaultPosition;
  mesh.position.copy(knownPosition); mesh.castShadow = true; chamber.add(mesh);
  roomInteractions.push({id:entity.id,entity,kind,position:knownPosition.clone(),count,x:knownPosition.x,z:knownPosition.z});
  const character=characterModel(entity.id);
  const label = sprite(`${kind.toUpperCase()} · ${field(entity,"short_description",String(entity.id))}${count>1?` ×${count}`:""}`); label.position.copy(mesh.position).add(new THREE.Vector3(0,character?3.05:1,0)); chamber.add(label);
  if (character) {
    const hostile=HOSTILE_IDS.has(entity.id);const ring = new THREE.Mesh(new THREE.TorusGeometry(hostile?1.0:.72,.07,8,32),new THREE.MeshBasicMaterial({color:hostile?0xff3030:0xe56b50}));
    ring.rotation.x = Math.PI / 2; ring.position.set(knownPosition.x,.04,knownPosition.z); chamber.add(ring);
    mesh.visible = false;
    void addModel(character.path,generation,model=>{model.position.set(knownPosition.x,0,knownPosition.z);model.rotation.y=Math.atan2(-knownPosition.x,-knownPosition.z);const motion={id:entity.id,root:model,head:model.getObjectByName("Head"),kind:character.animation,baseY:0,baseRotationY:model.rotation.y};characterMotions.push(motion);if(entity.id===3998)dummyVisual=model;if(hostile)activeHostileVisual=model;});
  } else if (entity.id === 3985) {
    mesh.visible = false;
    label.position.set(-2.6,3.25,-8.35);
    void addModel("/models/generated/old_parchment_3985.glb", generation, model => { model.position.set(-2.6,2.05,-8.55); model.rotation.y = Math.PI; });
  } else if(entity.id===72){mesh.visible=false;addKnifeModel(knownPosition);}
  else if(entity.id===3991||entity.id===3992)mesh.visible=false;
}

function sprite(text: string) { const c=document.createElement("canvas"); c.width=512;c.height=64; const x=c.getContext("2d")!; x.fillStyle="#070909cc";x.fillRect(0,0,512,64);x.fillStyle="#eadcae";x.font="25px sans-serif";x.textAlign="center";x.fillText(text.slice(0,38),256,41); const t=new THREE.CanvasTexture(c); const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true}));s.scale.set(4,.5,1);return s; }
function spawnCombatText(text:string,color:string,position:THREE.Vector3){const canvas=document.createElement("canvas");canvas.width=256;canvas.height=96;const context=canvas.getContext("2d")!;context.font="bold 54px Arial";context.textAlign="center";context.strokeStyle="#080909";context.lineWidth=8;context.strokeText(text,128,62);context.fillStyle=color;context.fillText(text,128,62);const texture=new THREE.CanvasTexture(canvas),value=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,transparent:true,depthTest:false}));value.position.copy(position).add(new THREE.Vector3(0,2.8,0));value.scale.set(1.8,.68,1);chamber.add(value);floatingCombatTexts.push({sprite:value,life:1});}
function animateCombatText(dt:number){for(let i=floatingCombatTexts.length-1;i>=0;i--){const effect=floatingCombatTexts[i];effect.life-=dt;effect.sprite.position.y+=dt*1.1;(effect.sprite.material as THREE.SpriteMaterial).opacity=Math.max(0,effect.life);if(effect.life<=0){chamber.remove(effect.sprite);floatingCombatTexts.splice(i,1);}}}

function entity(id: number): Entity | undefined { return [...world.npcs,...world.items].find(candidate=>candidate.id===id); }
const ARENA_GONG:Entity={id:-4168,stable_id:"interaction:arena-gong",fields:[{name:"short_description",value:"arena gong",confidence:"confirmed"},{name:"long_description",value:"A heavy brass gong used to summon a free arena opponent. Press E or type RING GONG.",confidence:"confirmed"}]};
function currentCharacterStats(){return characterStats(playerRace,playerClass,progression.level);}
function knownSpells():RoseSpell[]{const ids=STARTER_SPELL_IDS[playerClass];return spellFixture?.spells.filter(spell=>ids.includes(spell.id))??[];}
function sphereProficiencies():Record<number,number>{const base=playerClass==="Mage"?48:playerClass==="Priest"?45:playerClass==="Scholar"?39:playerClass==="Gypsy"?31:25;const result:Record<number,number>={1:base,2:base,3:base,4:base,5:base,6:base};if(playerClass==="Mage")result[1]+=8;if(playerClass==="Priest")result[2]+=10;for(const sphere of Object.keys(result))result[Number(sphere)]+=progression.level*2;return result;}
function isMobDefeated(key:string){const until=defeatedMobs.get(key);if(until===undefined)return false;if(performance.now()<until)return true;defeatedMobs.delete(key);return false;}
function rebuildPlayerAvatar(){if(playerAvatar)scene.remove(playerAvatar.root);playerAvatar=createPlayerAvatar(playerRace,playerClass);playerAvatar.root.position.copy(playerPosition);setAvatarEquipment(playerAvatar,equippedWeapon);scene.add(playerAvatar.root);}
function updateCharacterPreview(){const race=(RACES.includes(characterRaceSelect.value as PlayerRace)?characterRaceSelect.value:"Human") as PlayerRace,playerClassValue=(CLASSES.includes(characterClassSelect.value as PlayerClass)?characterClassSelect.value:"Warrior") as PlayerClass,stats=characterStats(race,playerClassValue),attributes=characterAttributes(race,playerClassValue);characterPreview.textContent=`${stats.maxHealth} health · ${stats.maxEndurance} movement · ${stats.maxMana} mana · ${attributes.strength} STR · ${attributes.dexterity} DEX · ${attributes.constitution} CON`;}
function cleanDescription(text:string){return text.replace(/\r/g,"\n").replace(/\n\s*\n\s*\d{4,}\s*\n[\s\S]*$/," ").trim();}
function showInteraction(heading: string, text: string, pinned=true) { interactionPinned=pinned;interactionTitle.textContent=heading; interactionText.textContent=cleanDescription(text); interactionPanel.hidden=false; }
function renderPlayerStatus(){const stats=currentCharacterStats(),hostile=combatTargetId?hostileStats(combatTargetId):undefined;playerStatus.replaceChildren();const titleLine=document.createElement("div");titleLine.className="hud-title";titleLine.textContent=`${playerName} · Level ${progression.level} ${playerRace} ${playerClass}`;playerStatus.append(titleLine);const meter=(label:string,value:number,max:number,kind:string)=>{const row=document.createElement("div");row.className="hud-row";const left=document.createElement("span"),right=document.createElement("span");left.textContent=label;right.textContent=`${Math.ceil(value)}/${max}`;row.append(left,right);const track=document.createElement("div");track.className=`meter ${kind}`;const fill=document.createElement("i");fill.style.width=`${Math.max(0,Math.min(100,value/max*100))}%`;track.append(fill);playerStatus.append(row,track);};meter("HEALTH",playerHealth,stats.maxHealth,"health");meter("MOVEMENT",playerEndurance,stats.maxEndurance,"endurance");meter("MANA",playerMana,stats.maxMana,"mana");meter("EXPERIENCE",progression.experience,progression.nextLevelExperience,"experience");const gear=document.createElement("div");gear.className="hud-row";gear.textContent=`Weapon: ${equippedWeapon?EQUIPMENT[equippedWeapon].name:"fists"} · Armor: ${equippedArmor?EQUIPMENT[equippedArmor].name:"clothes"}`;playerStatus.append(gear);const combat=document.createElement("div");combat.className="hud-row";combat.textContent=hostile?`Fighting ${hostile.name} ${combatTargetHealth}/${hostile.maxHealth}`:combatTargetId===3998?`Dummy ${dummyHealth}/30`:"Peaceful";playerStatus.append(combat);}
function panelSummary(values:readonly [string,string][]) {const summary=document.createElement("div");summary.className="panel-summary";for(const [label,value] of values){const card=document.createElement("div");card.className="summary-card";const strong=document.createElement("strong");strong.textContent=value;card.append(strong,label);summary.append(card);}return summary;}
function statSection(title:string,rows:readonly [string,string][]) {const section=document.createElement("section");section.className="stat-section";const heading=document.createElement("h3");heading.textContent=title;const grid=document.createElement("div");grid.className="stat-grid";for(const [label,value] of rows){const name=document.createElement("span"),amount=document.createElement("span");name.textContent=label;amount.textContent=value;grid.append(name,amount);}section.append(heading,grid);return section;}
function setEquipment(slot:EquipmentSlot,id?:EquipmentId){if(slot==="weapon"){equippedWeapon=id;if(playerAvatar)setAvatarEquipment(playerAvatar,equippedWeapon);}else equippedArmor=id;renderPlayerStatus();renderGamePanel();}
function renderInventoryPanel(){const stats=currentCharacterStats(),weight=inventoryWeight(ownedEquipment);gamePanelTitle.textContent="Inventory & equipment";gamePanelContent.replaceChildren(panelSummary([["carried weight",`${weight}/${stats.carryCapacity} troys`],["weapon",equippedWeapon?EQUIPMENT[equippedWeapon].name:"empty hands"],["armor",equippedArmor?EQUIPMENT[equippedArmor].name:"ordinary clothes"]]));const list=document.createElement("div");list.className="inventory-list";if(!ownedEquipment.size){const empty=document.createElement("div");empty.className="empty-state";empty.textContent="Your pack is empty. The training route contains a knife, and defeated creatures may drop equipment.";list.append(empty);}for(const id of ownedEquipment){const item=EQUIPMENT[id],isEquipped=equippedWeapon===id||equippedArmor===id,row=document.createElement("article");row.className="inventory-item";const copy=document.createElement("div"),heading=document.createElement("h3"),description=document.createElement("p"),meta=document.createElement("div"),button=document.createElement("button");heading.textContent=item.name;description.textContent=item.description;meta.className="item-meta";meta.textContent=`${item.slot.toUpperCase()} · ${item.weight} troys${item.damage?` · ${item.damageMin??item.damage}–${item.damage} damage`:""}${item.armor?` · +${item.armor} absorption`:""}`;copy.append(heading,description,meta);button.className=`panel-action${isEquipped?" secondary":""}`;button.textContent=isEquipped?"Unequip":"Equip";button.addEventListener("click",()=>setEquipment(item.slot,isEquipped?undefined:item.id));row.append(copy,button);list.append(row);}gamePanelContent.append(list);}
function renderCharacterPanel(){const stats=currentCharacterStats(),attributes=characterAttributes(playerRace,playerClass),skills=characterSkills(playerRace,playerClass);gamePanelTitle.textContent=`${playerName} · character`;gamePanelContent.replaceChildren(panelSummary([["level",String(progression.level)],["race",playerRace],["walk of life",playerClass]]));const sections=document.createElement("div");sections.className="stat-sections";sections.append(statSection("Attributes",ATTRIBUTE_NAMES.map(name=>[name[0].toUpperCase()+name.slice(1),String(attributes[name])])),statSection("Derived statistics",[["Health",`${Math.ceil(playerHealth)} / ${stats.maxHealth}`],["Movement",`${Math.ceil(playerEndurance)} / ${stats.maxEndurance}`],["Mana",`${Math.ceil(playerMana)} / ${stats.maxMana}`],["Attack damage",String(attackDamage(stats,equippedWeapon?EQUIPMENT[equippedWeapon]:undefined))],["Attack delay",`${stats.attackInterval.toFixed(2)} seconds`],["Armor / absorption",String(effectiveArmor(stats,equippedArmor?EQUIPMENT[equippedArmor]:undefined))],["Encumbrance",`${inventoryWeight(ownedEquipment)} / ${stats.carryCapacity} troys`],["Experience",`${progression.experience} / ${progression.nextLevelExperience}`]]),statSection("Proficiencies",skills.map(skill=>[`${skill.name} (${skill.prime.slice(0,3).toUpperCase()})`,`${skill.raw} → ${skill.adjusted}`])));const note=document.createElement("div");note.className="rules-note";note.textContent="Rose source evidence defines these eight attributes, six starting walks of life, prime-requisite skills, encumbrance, mana, health, armor and attack delays. Exact original numeric formulas remain undecoded; this prototype labels and tests its current balancing rules separately.";gamePanelContent.append(sections,note);}
function renderSpellPanel(){gamePanelTitle.textContent="Spellbook";const list=document.createElement("div");list.className="spell-list";for(const spell of knownSpells()){const card=document.createElement("article"),heading=document.createElement("h3"),description=document.createElement("p"),meta=document.createElement("div"),button=document.createElement("button");card.className="spell-card";heading.textContent=spell.name;const effect=spell.effects[0];description.textContent=isHealingSpell(spell)?`Restores ${effect?.dice_count??0}–${effect?.roll_min??0} health per caster level.`:isDamageSpell(spell)?`Deals ${effect?.dice_count??0} rolls of ${effect?.roll_min??0}–${effect?.roll_max??0} damage.`:"Invokes a recovered spell effect not yet supported by this client.";meta.className="spell-meta";meta.textContent=`${spell.sphere_name.toUpperCase()} · ${spell.mana_cost} mana · ${castingThreshold(spell,sphereProficiencies(),playerClass,progression.level)}% cast · base delay ${spell.base_recovery}`;button.textContent=isHealingSpell(spell)?"Cast on self":"Cast at target";button.disabled=playerMana<spell.mana_cost||spellRecovery>0||(!isHealingSpell(spell)&&combatTargetId===undefined);button.addEventListener("click",()=>{castSpell(spell);renderSpellPanel();});card.append(heading,description,meta,button);list.append(card);}const note=document.createElement("div");note.className="rules-note";note.textContent="Mana cost, success threshold, damage/healing dice, and base delay come from RCI_SPEL and the decompiled Rose DLL. Starter spell access, sphere starting values, and the bounded recovery reduction are prototype rules pending further decoding.";gamePanelContent.replaceChildren(list,note);}
function renderGamePanel(){if(openPanel==="inventory")renderInventoryPanel();else if(openPanel==="character")renderCharacterPanel();else if(openPanel==="spells")renderSpellPanel();}
function openGameMenu(panel:"inventory"|"character"|"spells"){openPanel=panel;gamePanel.hidden=false;document.body.classList.add("menu-open");keys.clear();if(document.pointerLockElement)void document.exitPointerLock();renderGamePanel();}
function closeGameMenu(){openPanel=undefined;gamePanel.hidden=true;document.body.classList.remove("menu-open");}
function setInputMode(mode:"mouse"|"command"){inputMode=mode;closeGameMenu();document.body.classList.toggle("command-mode",mode==="command");controlModeButton.textContent=mode==="command"?"Return to mouse":"Commands · Enter";if(mode==="command"){keys.clear();if(document.pointerLockElement)void document.exitPointerLock();commandInput.focus();}else{commandInput.blur();if(characterCreated)void canvas.requestPointerLock();}}
function renderTutorial() {
  tutorial.hidden=currentRoomId!==INITIAL_ROOM_ID;
  if(tutorial.hidden)return;
  const step=(done:boolean,text:string)=>`${done?"✓":"○"} ${text}`;
  tutorial.textContent=["PASSAGES OF LEARNING",step(tutorialProgress.has("look"),"Type LOOK"),step(tutorialProgress.has("old-man"),"Examine or talk to the old man"),step(tutorialProgress.has("parchment"),"Read the old parchment"),step(tutorialProgress.has("west"),"Leave through the west passage")].join("\n");
}
function performInitialRoomAction(action: InitialRoomAction) {
  const room=world.rooms.find(candidate=>candidate.id===INITIAL_ROOM_ID)!; const oldMan=entity(3993); const parchment=entity(3985);
  if(action==="look-room") { tutorialProgress.add("look"); showInteraction(field(room,"short_description","The training room"),field(room,"long_description","You look around.")); }
  else if(action==="inspect-old-man") { tutorialProgress.add("old-man"); showInteraction(field(oldMan!,"short_description","old man"),field(oldMan!,"long_description","The old man points toward the parchment.")); }
  else if(action==="talk-old-man") { tutorialProgress.add("old-man"); showInteraction("The old man gestures",field(oldMan!,"long_description","The old man points toward the parchment.")); }
  else if(action==="read-parchment") { tutorialProgress.add("parchment"); showInteraction(field(parchment!,"short_description","old parchment"),field(parchment!,"long_description","The parchment describes movement commands.")); }
  else showInteraction("old parchment","The parchment is firmly tacked to the wall. You cannot take it, but you can READ it.");
  renderTutorial();
}
function interactNearby() {
  const forward=new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(0,yaw,0));
  const target=findFacingEntity({x:playerPosition.x,z:playerPosition.z},{x:forward.x,z:forward.z},roomInteractions);
  if(target)interactEntity(target);else renderUi("Nothing is close enough to interact with.");
}
function interactEntity(target:RoomInteraction){
  if(target.entity.id===3993)return performInitialRoomAction("inspect-old-man");
  if(target.entity.id===3985)return performInitialRoomAction("read-parchment");
  if(target.entity.id===72){inventory.add(72);ownedEquipment.add("training-knife");equippedWeapon="training-knife";if(playerAvatar)setAvatarEquipment(playerAvatar,equippedWeapon);showInteraction("You equip a training knife",field(target.entity,"long_description","You take one of the knives."));renderPlayerStatus();return;}
  if(target.entity.id===3998)return startDummyCombat();
  if(target.entity.id===ARENA_GONG.id)return ringArenaGong();
  if(HOSTILE_IDS.has(target.entity.id))return startHostileCombat(target.entity.id);
  showInteraction(field(target.entity,"short_description",String(target.entity.id)),field(target.entity,"long_description","You see nothing unusual."));
}
function updateInteractionPrompt(forward: THREE.Vector3) {
  const position={x:playerPosition.x,z:playerPosition.z},direction={x:forward.x,z:forward.z};
  const target=findFacingEntity(position,direction,roomInteractions,9); const nearby=findFacingEntity(position,direction,roomInteractions);
  if(nearby?.entity.id!==activeNearbyEntityId){activeNearbyEntityId=nearby?.entity.id;interactionPrompt.hidden=!nearby;if(nearby){const action=nearby.entity.id===72?"take knife":nearby.entity.id===3998?"attack dummy":nearby.entity.id===ARENA_GONG.id?"ring gong":HOSTILE_IDS.has(nearby.entity.id)?`attack ${field(nearby.entity,"short_description","opponent")}`:"interact";interactionPrompt.textContent=`E · ${action}`;}}
  if(target?.entity.id===activeEntityId)return;
  activeEntityId=target?.entity.id;
  if(target){
    showInteraction(field(target.entity,"short_description",String(target.entity.id)),field(target.entity,"long_description","You see nothing unusual."),false);
  }else if(!interactionPinned)interactionPanel.hidden=true;
}
function renderProximityActions(){
  const nearby=roomInteractions.filter(target=>distance2d(playerPosition,target.position)<=4.2).sort((a,b)=>distance2d(playerPosition,a.position)-distance2d(playerPosition,b.position));
  const exits=exitTriggers.filter(exit=>distance2d(playerPosition,exit.position)<=4.3);
  const signature=[...nearby.map(target=>`${target.id}:${Math.round(distance2d(playerPosition,target.position))}`),...exits.map(exit=>`x${exit.edge.direction}`),combatTargetId,Math.ceil(spellRecovery)].join("|");
  if(signature===proximitySignature)return;proximitySignature=signature;proximityButtons.replaceChildren();
  const button=(label:string,action:()=>void,danger=false)=>{const element=document.createElement("button");element.textContent=label;element.classList.toggle("danger",danger);element.addEventListener("click",action);proximityButtons.append(element);};
  for(const target of nearby.slice(0,3)){const name=field(target.entity,"short_description",String(target.id));if(HOSTILE_IDS.has(target.id)){button(`Attack ${name}`,()=>startHostileCombat(target.id),true);for(const spell of knownSpells().filter(isDamageSpell).slice(0,2))button(`${spell.name} (${spell.mana_cost})`,()=>castSpell(spell,target.id),true);}else button(target.id===72?"Take knife":target.id===ARENA_GONG.id?"Ring gong":target.id===3998?"Attack dummy":`Inspect ${name}`,()=>interactEntity(target),target.id===3998);}
  for(const exit of exits.slice(0,2))button(`Go ${exit.edge.direction}`,()=>attemptGo(exit.edge,false));
  proximityActions.hidden=proximityButtons.childElementCount===0;
}
function startDummyCombat(){if(currentRoomId!==3982)return showInteraction("No target","The wooden practice dummy is not here.");combatTargetId=3998;combatClock=0;showInteraction("Combat started",`You attack the wooden dummy${inventory.has(72)?" with your knife":" with your bare hands"}. Type STOP to disengage.`);renderPlayerStatus();}
function ringArenaGong(){if(currentRoomId!==4168)return showInteraction("No gong here","The Pendelhaven arena gong is not here.");arenaRound+=1;arenaOpponentId=arenaOpponent(arenaRound);const stats=hostileStats(arenaOpponentId)!;combatTargetHealth=stats.maxHealth;combatTargetId=undefined;combatClock=enemyCombatClock=0;buildRoom(undefined,true);showInteraction("The arena gong booms",`Smoke curls from the summoning circle. A ${stats.name} materializes with ${stats.maxHealth} health. Aim at it and press E, or type ATTACK ${stats.name.toUpperCase()}.`);renderPlayerStatus();}
function startHostileCombat(id:number){const stats=hostileStats(id),present=roomInteractions.some(target=>target.id===id);if(!stats||!present||(currentRoomId===4168&&arenaOpponentId!==id)||isMobDefeated(`${currentRoomId}:${id}`))return showInteraction("No target","That opponent is not available here.");if(combatTargetId!==id)combatTargetHealth=stats.maxHealth;if(combatTargetHealth<=0)return showInteraction("Opponent defeated",currentRoomId===4168?"Ring the gong to summon the next arena opponent.":"This area is temporarily safe.");combatTargetId=id;combatClock=enemyCombatClock=0;showInteraction("Combat started",`You engage the ${stats.name} with ${equippedWeapon?`your ${EQUIPMENT[equippedWeapon].name}`:"your bare hands"}. It will fight back. Type STOP to disengage.`);renderPlayerStatus();}
function castSpell(spell:RoseSpell,targetId=combatTargetId){
  if(spellRecovery>0)return showInteraction("Still recovering",`You can cast again in ${spellRecovery.toFixed(1)} seconds.`);
  if(playerMana<spell.mana_cost)return showInteraction("Not enough mana",`${spell.name} requires ${spell.mana_cost} mana.`);
  if(isDamageSpell(spell)){if(targetId===undefined)return showInteraction("No spell target","Engage or approach an opponent before casting a damaging spell.");const target=roomInteractions.find(candidate=>candidate.id===targetId);if(!target||distance2d(playerPosition,target.position)>6.5)return showInteraction("Target out of range","Move closer before casting.");if(HOSTILE_IDS.has(targetId)&&combatTargetId!==targetId)startHostileCombat(targetId);else if(targetId===3998)combatTargetId=3998;}
  playerMana-=spell.mana_cost;spellRecovery=recoverySeconds(spell,sphereProficiencies()[spell.sphere]??0);const threshold=castingThreshold(spell,sphereProficiencies(),playerClass,progression.level),roll=1+Math.floor(Math.random()*100);
  if(roll>threshold){showInteraction(`${spell.name} fails`,`Casting roll ${roll} exceeded ${threshold}. ${spell.mana_cost} mana is spent and you must recover for ${spellRecovery.toFixed(1)} seconds.`);renderPlayerStatus();return;}
  const magnitude=spellMagnitude(spell,progression.level);
  if(isHealingSpell(spell)){const stats=currentCharacterStats(),before=playerHealth;playerHealth=Math.min(stats.maxHealth,playerHealth+magnitude);spawnCombatText(`+${Math.ceil(playerHealth-before)}`,"#7dff9b",playerPosition);showInteraction(spell.name,`Casting roll ${roll}/${threshold}. You recover ${Math.ceil(playerHealth-before)} health.`);}
  else if(targetId===3998){dummyHealth=Math.max(0,dummyHealth-magnitude);spawnCombatText(`-${magnitude}`,"#8dcfff",dummyVisual?.position??new THREE.Vector3());showInteraction(spell.name,`Casting roll ${roll}/${threshold}. The spell deals ${magnitude} damage. Dummy: ${dummyHealth}/30 HP`);if(dummyHealth===0)combatTargetId=undefined;}
  else if(targetId!==undefined){const stats=hostileStats(targetId);combatTargetHealth=Math.max(0,combatTargetHealth-magnitude);const targetPosition=roomInteractions.find(target=>target.id===targetId)?.position??new THREE.Vector3();spawnCombatText(`-${magnitude}`,"#8dcfff",targetPosition);showInteraction(spell.name,`Casting roll ${roll}/${threshold}. The spell deals ${magnitude} damage to ${stats?.name??"the target"}.`);if(combatTargetHealth===0&&stats)completeHostileVictory(targetId,stats.name);}
  renderPlayerStatus();
}
function stopCombat(){combatTargetId=undefined;pursuingMobId=undefined;pursuitRoomId=undefined;combatClock=enemyCombatClock=0;showInteraction("Combat stopped","You stop attacking. A nearby hostile may engage again if provoked.");renderPlayerStatus();}
function respawnPlayer(){const stats=currentCharacterStats();playerHealth=stats.maxHealth;playerEndurance=stats.maxEndurance;playerMana=stats.maxMana;combatTargetId=undefined;pursuingMobId=undefined;pursuitRoomId=undefined;arenaOpponentId=undefined;combatTargetHealth=0;combatClock=enemyCombatClock=0;currentRoomId=4169;buildRoom();playerPosition.set(4.5,0,4.5);yaw=-Math.PI*3/4;showInteraction("You awaken in Pendelhaven Hospice","Vivian and the healers restore your health, movement, and mana. Your experience and equipment remain with you.");renderPlayerStatus();}
function flashPlayerDamage(){document.body.classList.remove("hurt");void document.body.offsetWidth;document.body.classList.add("hurt");setTimeout(()=>document.body.classList.remove("hurt"),260);}
function completeHostileVictory(id:number,name:string){const reward=rewardForMob(id);combatTargetId=undefined;pursuingMobId=undefined;pursuitRoomId=undefined;if(activeHostileVisual)activeHostileVisual.rotation.z=Math.PI/2;let rewardText="";if(reward){const result=gainExperience(progression,reward.experience);progression=result.progression;ownedEquipment.add(reward.loot);rewardText=`\n\n+${reward.experience} XP · found ${EQUIPMENT[reward.loot].name}. Type EQUIP ${EQUIPMENT[reward.loot].name.toUpperCase()}.`;if(result.levelsGained){const oldMax=currentCharacterStats().maxHealth;const newStats=characterStats(playerRace,playerClass,progression.level);playerHealth=Math.min(newStats.maxHealth,playerHealth+Math.max(12,newStats.maxHealth-oldMax));rewardText+=`\nLevel up! You are now level ${progression.level}.`;}}
  if(currentRoomId===4168){victories+=1;rewardText+=`\nArena victory ${victories}. Ring the gong for another opponent.`;}else{defeatedMobs.set(`${currentRoomId}:${id}`,performance.now()+30000);rewardText+="\nThis creature will respawn in about 30 seconds.";}showInteraction("Victory",`The ${name} collapses.${rewardText}`);renderPlayerStatus();}
function advanceHostilePursuit(dt:number){if(!combatTargetId||!HOSTILE_IDS.has(combatTargetId))return;const interaction=roomInteractions.find(target=>target.id===combatTargetId);if(!interaction)return;const next=chaseStep(interaction.position,playerPosition,2.35,dt);interaction.position.set(next.x,interaction.position.y,next.z);interaction.x=next.x;interaction.z=next.z;const motion=characterMotions.find(candidate=>candidate.id===combatTargetId);if(motion){motion.root.position.x=next.x;motion.root.position.z=next.z;motion.root.rotation.y=Math.atan2(playerPosition.x-next.x,playerPosition.z-next.z);}}
function advanceCombat(dt:number){const playerStats=currentCharacterStats(),attackInterval=playerStats.attackInterval;if(combatTargetId===3998){combatClock+=dt;if(combatClock<attackInterval)return;combatClock-=attackInterval;const strike=resolveMeleeAttack(playerRace,playerClass,progression.level,equippedWeapon?EQUIPMENT[equippedWeapon]:undefined,0,inventoryWeight(ownedEquipment));if(!strike.hit){spawnCombatText("MISS","#d8d2bf",dummyVisual?.position??new THREE.Vector3());showInteraction("You miss the wooden dummy",`Attack roll ${strike.roll} exceeded ${strike.chance}.`);return;}dummyHealth=Math.max(0,dummyHealth-strike.damage);spawnCombatText(`-${strike.damage}`,"#ffd66b",dummyVisual?.position??new THREE.Vector3());showInteraction("You strike the wooden dummy",`Attack roll ${strike.roll}/${strike.chance}. Your attack deals ${strike.damage} damage.\n\nDummy: ${dummyHealth}/30 HP`);if(dummyHealth===0){combatTargetId=undefined;interactionText.textContent+="\n\nThe battered dummy yields. Practice complete.";}renderPlayerStatus();return;}const stats=combatTargetId?hostileStats(combatTargetId):undefined;if(!stats)return;const targetId=combatTargetId!,targetInteraction=roomInteractions.find(target=>target.id===targetId);if(!targetInteraction||distance2d(playerPosition,targetInteraction.position)>2.35)return;combatClock+=dt;enemyCombatClock+=dt;let message="";if(combatClock>=attackInterval){combatClock-=attackInterval;const strike=resolveMeleeAttack(playerRace,playerClass,progression.level,equippedWeapon?EQUIPMENT[equippedWeapon]:undefined,stats.armor,inventoryWeight(ownedEquipment));if(strike.hit){combatTargetHealth=Math.max(0,combatTargetHealth-strike.damage);spawnCombatText(`-${strike.damage}`,"#ffd66b",targetInteraction.position);message=`You strike the ${stats.name} for ${strike.damage} damage (${strike.roll}/${strike.chance}).`;if(combatTargetHealth===0){completeHostileVictory(targetId,stats.name);return;}}else{spawnCombatText("MISS","#d8d2bf",targetInteraction.position);message=`You miss the ${stats.name} (${strike.roll}/${strike.chance}).`;}}if(enemyCombatClock>=stats.attackInterval){enemyCombatClock-=stats.attackInterval;const damage=receivedDamage(stats.damage,playerStats,equippedArmor?EQUIPMENT[equippedArmor]:undefined);playerHealth=Math.max(0,playerHealth-damage);spawnCombatText(`-${damage}`,"#ff5b4d",playerPosition);flashPlayerDamage();message+=`${message?"\n":""}The ${stats.name} hits you for ${damage} damage.`;if(playerHealth===0){respawnPlayer();return;}}if(message)showInteraction(`Fighting ${stats.name}`,`${message}\n\nYou: ${playerHealth}/${playerStats.maxHealth} HP · ${stats.name}: ${combatTargetHealth}/${stats.maxHealth} HP`);renderPlayerStatus();}
function runInitialRoomDiagnostics() {
  const paths=["/models/generated/training_room_3976.glb","/models/generated/old_man_3993.glb","/models/generated/old_parchment_3985.glb"];
  const checks=[
    [paths.every(path=>loadedModels.has(path)),"room, NPC, and item models loaded"],
    [world.edges.filter(edge=>edge.from_room===INITIAL_ROOM_ID&&edge.direction==="W"&&!edge.hidden).length===1,"one canonical visible west exit"],
    [initialRoomCommand("look at old man")==="inspect-old-man"&&initialRoomCommand("read parchment")==="read-parchment","tutorial commands mapped"],
    [findInitialRoomTarget({x:2.7,z:-4.5},{x:0,z:-1})==="old-man","proximity and facing targeting active"],
    [constrainInitialRoomMovement({x:99,z:-99}).x===8.45,"room wall constraints active"],
  ] as const;
  showInteraction("Room 3976 diagnostics",checks.map(([passed,label])=>`${passed?"PASS":"FAIL"} · ${label}`).join("\n"));
}

function buildRoom(entryEdge?:Edge,preserveCamera=false) {
  const previousPosition=playerPosition.clone(),previousYaw=yaw,previousPitch=pitch;
  const generation = ++roomGeneration; chamber.clear(); exitTriggers.length = 0; roomInteractions.length=0;ambientMotions.length=0;characterMotions.length=0;floatingCombatTexts.length=0;dummyVisual=undefined;activeHostileVisual=undefined;
  if(preserveCamera){playerPosition.copy(previousPosition);yaw=previousYaw;pitch=previousPitch;}else{const arrivalDirection=entryEdge?edgesFrom(world,currentRoomId,true).find(edge=>edge.to_room===entryEdge.from_room)?.direction:undefined;const spawn=entryEdge?entrySpawnAfterTravel(entryEdge.direction,arrivalDirection):undefined;if(spawn){playerPosition.set(spawn.x,0,spawn.z);yaw=spawn.yaw;pitch=0;}else{playerPosition.set(0,0,0);yaw=0;pitch=0;}}if(playerAvatar)playerAvatar.root.position.copy(playerPosition);
  const followedHere=pursuingMobId!==undefined&&pursuitRoomId===currentRoomId;
  if(currentRoomId!==3982&&currentRoomId!==4168&&!followedHere){combatTargetId=undefined;combatClock=enemyCombatClock=0;}else if(followedHere){combatTargetId=pursuingMobId;combatTargetHealth=pursuingMobHealth;}else if(currentRoomId===3982&&dummyHealth<=0)dummyHealth=30;
  const modeledRoom=trainingRouteModel(currentRoomId);
  if (modeledRoom) {
    scene.background=new THREE.Color(modeledRoom.background);scene.fog=new THREE.Fog(modeledRoom.background,12,29);torch.color.setHex(modeledRoom.light);skyLight.intensity=1.55;
    void addModel(modeledRoom.path, generation);
  } else {
    scene.background=new THREE.Color(0x07090b);scene.fog=new THREE.Fog(0x07090b,12,29);torch.color.setHex(0xffb45c);skyLight.intensity=1.6;
    addBox(new THREE.Vector3(18,.3,18), new THREE.Vector3(0,-.18,0),0x3b3427); addBox(new THREE.Vector3(18,.3,18),new THREE.Vector3(0,5.1,0),0x24272a);
  }
  const visible = edgesFrom(world,currentRoomId,showHidden); const groups = new Map<string,Edge[]>();
  for (const edge of visible) groups.set(edge.direction,[...(groups.get(edge.direction)??[]),edge]);
  for (const [direction, group] of groups) group.forEach((edge,index) => {
    const base=positions[direction] ?? new THREE.Vector3(); const tangent=new THREE.Vector3(-base.z,0,base.x).normalize(); const at=base.clone().addScaledVector(tangent,(index-(group.length-1)/2)*1.7);
    if (modeledRoom) {
      const label=sprite(`${direction} → ${edge.to_room}`);label.position.copy(at).setY(3.5);chamber.add(label);
      exitTriggers.push({edge,position:at});
      return;
    }
    const arch=new THREE.Group(); const tint=edge.hidden?0x724c72:edge.door?0x87552f:world.rooms.find(r=>r.id===edge.to_room)?.scope==="stub"?0x376471:0x4e756d;
    const left=addBox(new THREE.Vector3(.35,2.8,.45),at.clone().addScaledVector(tangent,-.85).setY(1.4),tint); const right=addBox(new THREE.Vector3(.35,2.8,.45),at.clone().addScaledVector(tangent,.85).setY(1.4),tint); const top=addBox(new THREE.Vector3(2.05,.35,.45),at.clone().setY(2.8),tint); arch.add(left,right,top); chamber.add(arch);
    if (edge.door) addBox(new THREE.Vector3(1.3,2.3,.18),at.clone().setY(1.15),0x51301c);
    const label=sprite(`${direction}${group.length>1?` ${index+1}`:""} → ${edge.to_room}${edge.hidden?" · HIDDEN":""}`);label.position.copy(at).setY(3.5);chamber.add(label);
    exitTriggers.push({edge,position:at});
  });
  const roomSpawn=world.spawns.find(s=>s.id===currentRoomId); let markerIndex=0;
  for (const entry of roomSpawn?.entries??[]) { const list=entry.entity_type==="npc"?world.npcs:world.items; const e=list.find(x=>x.id===entry.entity_id); if(e&&!(entry.entity_type==="npc"&&HOSTILE_IDS.has(e.id)&&isMobDefeated(`${currentRoomId}:${e.id}`))) marker(e,entry.entity_type,markerIndex++,generation,entry.count); }
  if(followedHere&&!roomInteractions.some(target=>target.id===pursuingMobId)){const pursuer=entity(pursuingMobId!);if(pursuer)marker(pursuer,"npc",markerIndex++,generation,1);}
  if(currentRoomId===4168){const gongPosition=new THREE.Vector3(5.1,.7,-2.8);roomInteractions.push({id:ARENA_GONG.id,entity:ARENA_GONG,kind:"item",position:gongPosition,count:1,x:gongPosition.x,z:gongPosition.z});const gongLabel=sprite("INTERACT · arena gong");gongLabel.position.set(gongPosition.x,2.8,gongPosition.z);chamber.add(gongLabel);if(arenaOpponentId){const opponent=entity(arenaOpponentId);if(opponent)marker(opponent,"npc",markerIndex++,generation,1);}}
  if(modeledRoom)addRoomAnimation(modeledRoom.animation);
  interactionPanel.hidden=true; interactionPinned=false; activeEntityId=undefined; activeNearbyEntityId=undefined; interactionPrompt.hidden=true; renderUi(); renderTutorial(); renderPlayerStatus();
}

function renderUi(message="") {
  const room=world.rooms.find(r=>r.id===currentRoomId)!; const all=world.edges.filter(e=>e.from_room===currentRoomId); const visible=edgesFrom(world,currentRoomId,showHidden);
  title.textContent=`${field(room,"short_description",room.scope==="stub"?"Boundary room":"Untitled room")}  [${room.id}]`;
  description.textContent=field(room,"long_description",room.scope==="stub"?"This is a skeletal boundary stub. Travel can continue only along exported authoritative edges.":"No description was decoded.");
  exitsElement.textContent=`Exits: ${visible.map(e=>`${e.direction}→${e.to_room}${e.door?" [door]":""}${e.hidden?" [hidden]":""}`).join(" · ") || "none"}${message?`  — ${message}`:""}`;
  developer.hidden=!developerVisible; developer.textContent=[`room ${room.stable_id}`,`scope ${room.scope}`,`region ${room.display?.region??"unknown"} (${room.display?.region_name??"unknown"})`,`source row ${room.provenance?.source_row_id??"unknown"}`,`edges ${visible.length} visible / ${all.length} total`,`parallel directions ${[...new Set(all.filter((e,i,a)=>a.findIndex(x=>x.direction===e.direction)!==i).map(e=>e.direction))].join(", ")||"none"}`,`hidden ${showHidden?"shown":"suppressed"}`,`fixture ${world.fixture.id}`,`contract ${world.contract.name} ${world.contract.version}`].join("\n");
}

function attemptGo(edge:Edge,sprinting=false){const mob=combatTargetId&&HOSTILE_IDS.has(combatTargetId)?roomInteractions.find(target=>target.id===combatTargetId):undefined;const exit=exitTriggers.find(candidate=>candidate.edge===edge);if(exitBlocked(mob?.position,exit?.position??playerPosition,!!mob,sprinting)){showInteraction("Your escape is blocked",`The ${hostileStats(combatTargetId!)?.name??"creature"} cuts off the ${edge.direction} exit. Sprint with Shift to break through, or defeat it.`);return;}if(combatTargetId&&HOSTILE_IDS.has(combatTargetId)&&canMobFollow(edge,world.fixture.primary_room_ids)){pursuingMobId=combatTargetId;pursuingMobHealth=combatTargetHealth;pursuitRoomId=edge.to_room;}else{pursuingMobId=undefined;pursuitRoomId=undefined;}if(currentRoomId===INITIAL_ROOM_ID&&edge.direction==="W")tutorialProgress.add("west");currentRoomId=edge.to_room;buildRoom(edge);if(pursuingMobId)showInteraction("Pursued",`The ${hostileStats(pursuingMobId)?.name??"creature"} follows you through the passage.`);}
function go(edge:Edge){attemptGo(edge,false);}
function issue(raw: string) {
  const c=raw.trim().toLowerCase(); if(!c)return;
  if(currentRoomId===INITIAL_ROOM_ID&&(c==="diagnose"||c==="test room"))return runInitialRoomDiagnostics();
  const initialAction=currentRoomId===INITIAL_ROOM_ID?initialRoomCommand(c):undefined;
  if(initialAction)return performInitialRoomAction(initialAction);
  const action=gameplayCommand(c);
  if(action==="get-knife"){
    if(currentRoomId!==3980)return showInteraction("No knife here","You do not see a knife close enough to take.");
    inventory.add(72);ownedEquipment.add("training-knife");equippedWeapon="training-knife";if(playerAvatar)setAvatarEquipment(playerAvatar,equippedWeapon);showInteraction("You equip a training knife",field(entity(72)!,"long_description","You take one of the knives."));renderPlayerStatus();return;
  }
  if(action==="attack-dummy")return startDummyCombat();
  if(action==="ring-gong")return ringArenaGong();
  if(action==="stop-combat")return stopCombat();
  if(action==="inventory")return openGameMenu("inventory");
  if(c==="spells"||c==="spellbook")return openGameMenu("spells");
  if(c.startsWith("cast ")){const spell=findSpell(knownSpells(),c.slice(5));if(!spell)return showInteraction("Unknown spell","That spell is not in your spellbook. Type SPELLS to review known magic.");return castSpell(spell);}
  if(c.startsWith("equip ")||c.startsWith("arm ")){const item=findEquipment(c.replace(/^(equip|arm)\s+/,""));if(!item||!ownedEquipment.has(item.id))return showInteraction("Cannot equip","You do not own that equipment.");setEquipment(item.slot,item.id);showInteraction("Equipment changed",`You equip ${item.name}.`);return;}
  if(c.startsWith("unequip")||c.startsWith("remove ")||c==="disarm"){const requested=c.replace(/^(unequip|remove|disarm)\s*/,"");const slot:EquipmentSlot=requested.includes("armor")?"armor":"weapon";const removed=slot==="weapon"?equippedWeapon:equippedArmor;if(!removed)return showInteraction("Nothing equipped",`You have no ${slot} equipped.`);setEquipment(slot);showInteraction("Equipment changed",`You unequip ${EQUIPMENT[removed].name}.`);return;}
  if(["stats","score","st","attributes","skills","showprofs"].includes(c))return openGameMenu("character");
  const targetName=attackTargetName(c);if(targetName){const hostile=roomInteractions.find(target=>HOSTILE_IDS.has(target.id)&&matchesHostileName(target.id,targetName));if(hostile)return startHostileCombat(hostile.id);}
  if(c==="look"||c==="l")return renderUi("You look around.");
  if(c.startsWith("flee ")){const edge=travel(world,currentRoomId,c.slice(5),showHidden);if(!edge)return renderUi("No such visible exit.");if(playerEndurance<12)return showInteraction("Too exhausted to flee","Recover movement before forcing your way past an opponent.");playerEndurance-=12;return attemptGo(edge,true);}
  const edge=travel(world,currentRoomId,c,showHidden); if(edge)return go(edge);
  renderUi(commandDirection(c)?"No such visible exit.":`Unknown command: ${raw}`);
}

commandForm.addEventListener("submit",event=>{event.preventDefault();issue(commandInput.value);commandInput.value="";});
commandInput.addEventListener("focus",()=>{if(characterCreated&&inputMode!=="command")setInputMode("command");});
canvas.addEventListener("click",()=>{if(characterCreated)setInputMode("mouse");}); document.addEventListener("mousemove",e=>{if(document.pointerLockElement!==canvas)return;yaw-=e.movementX*.002;pitch=Math.max(-.8,Math.min(.8,pitch-e.movementY*.002));});
document.querySelectorAll<HTMLButtonElement>("[data-open-panel]").forEach(button=>button.addEventListener("click",()=>openGameMenu(button.dataset.openPanel as "inventory"|"character"|"spells")));
gamePanelClose.addEventListener("click",closeGameMenu);controlModeButton.addEventListener("click",()=>setInputMode(inputMode==="mouse"?"command":"mouse"));
addEventListener("keydown",e=>{if(["INPUT","SELECT","BUTTON"].includes((e.target as HTMLElement).tagName))return;if(e.code==="Enter"&&!e.repeat){e.preventDefault();setInputMode("command");return;}if(e.code==="Escape"&&openPanel){closeGameMenu();return;}if(e.code==="KeyI"&&!e.repeat){openGameMenu("inventory");return;}if(e.code==="KeyC"&&!e.repeat){openGameMenu("character");return;}if(e.code==="KeyK"&&!e.repeat){openGameMenu("spells");return;}if(openPanel)return;keys.add(e.code);if(e.code==="KeyE"&&!e.repeat)interactNearby();if(e.code==="KeyV"&&!e.repeat){vHeld=true;vZoomed=false;}if(e.key.toLowerCase()==="h"){showHidden=!showHidden;buildRoom(undefined,true);}if(e.key==="`"){developerVisible=!developerVisible;renderUi();}});addEventListener("keyup",e=>{keys.delete(e.code);if(e.code==="KeyV"&&vHeld){if(!vZoomed){thirdPerson=!thirdPerson;if(playerAvatar)playerAvatar.root.visible=thirdPerson;}vHeld=false;}});
addEventListener("wheel",e=>{if(!vHeld)return;e.preventDefault();thirdPersonDistance=adjustThirdPersonDistance(thirdPersonDistance,e.deltaY);vZoomed=true;thirdPerson=true;if(playerAvatar)playerAvatar.root.visible=true;},{passive:false});
addEventListener("resize",()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);composer.setSize(innerWidth,innerHeight);});
characterRaceSelect.addEventListener("change",updateCharacterPreview);characterClassSelect.addEventListener("change",updateCharacterPreview);updateCharacterPreview();
characterForm.addEventListener("submit",event=>{event.preventDefault();playerName=characterNameInput.value.trim()||"Adventurer";playerRace=(RACES.includes(characterRaceSelect.value as PlayerRace)?characterRaceSelect.value:"Human") as PlayerRace;playerClass=(CLASSES.includes(characterClassSelect.value as PlayerClass)?characterClassSelect.value:"Warrior") as PlayerClass;const stats=currentCharacterStats();playerHealth=stats.maxHealth;playerEndurance=stats.maxEndurance;playerMana=stats.maxMana;characterCreated=true;characterCreation.hidden=true;rebuildPlayerAvatar();renderPlayerStatus();});

let last=performance.now(), transitionCooldown=0,hudClock=0;
function frame(now:number){requestAnimationFrame(frame);const dt=Math.min((now-last)/1000,.05);last=now;spellRecovery=Math.max(0,spellRecovery-dt);const forward=new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(0,yaw,0)),right=new THREE.Vector3(1,0,0).applyEuler(new THREE.Euler(0,yaw,0)),move=new THREE.Vector3();if(characterCreated){if(keys.has("KeyW"))move.add(forward);if(keys.has("KeyS"))move.sub(forward);if(keys.has("KeyA"))move.sub(right);if(keys.has("KeyD"))move.add(right);}const moving=move.lengthSq()>.001;if(moving)move.normalize();const wantsRun=moving&&(keys.has("ShiftLeft")||keys.has("ShiftRight"))&&playerEndurance>0,isRunning=wantsRun&&playerEndurance>.1,stats=currentCharacterStats();playerEndurance=updateEndurance(playerEndurance,stats.maxEndurance,dt,isRunning,moving);playerMana=Math.min(stats.maxMana,playerMana+dt*(playerRace==="Gnome"?2:1));const proposed=playerPosition.clone().addScaledVector(move,dt*(isRunning?7.2:4));let constrained:{x:number;z:number};if(currentRoomId===INITIAL_ROOM_ID)constrained=constrainInitialRoomMovement({x:proposed.x,z:proposed.z});else constrained=constrainModeledMovement(currentRoomId,{x:playerPosition.x,z:playerPosition.z},{x:proposed.x,z:proposed.z});playerPosition.set(constrained.x,modeledFloorHeight(currentRoomId,constrained),constrained.z);if(playerAvatar){playerAvatar.root.position.copy(playerPosition);playerAvatar.root.visible=thirdPerson;if(moving)playerAvatar.root.rotation.y=Math.atan2(-move.x,-move.z);animatePlayerAvatar(playerAvatar,now/1000,moving,isRunning,combatTargetId!==undefined);playerAvatar.root.position.y+=playerPosition.y;}if(thirdPerson){const focus=playerPosition.clone().add(new THREE.Vector3(0,1.45,0)),desired=focus.clone().addScaledVector(forward,-thirdPersonDistance).add(new THREE.Vector3(0,2.25+pitch*2.2,0));camera.position.lerp(desired,1-Math.pow(.001,dt));camera.lookAt(focus);}else{camera.position.set(playerPosition.x,playerPosition.y+1.7,playerPosition.z);camera.rotation.set(pitch,yaw,0);}updateInteractionPrompt(forward);advanceHostilePursuit(dt);advanceCombat(dt);renderProximityActions();animateRoom(now);animateCentralMotions(now);animateCombatText(dt);transitionCooldown-=dt;if(transitionCooldown<=0){const hit=exitTriggers.find(x=>horizontalTriggerReached(playerPosition,x.position));if(hit){transitionCooldown=1;attemptGo(hit.edge,isRunning);}}hudClock-=dt;if(hudClock<=0){hudClock=.1;renderPlayerStatus();}composer.render();}

async function boot(){try{const [worldResponse,spellResponse]=await Promise.all([fetch("/private/pendelhaven-v1.json",{cache:"no-store"}),fetch("/private/spells-v1.json",{cache:"no-store"})]);if(!worldResponse.ok||!spellResponse.ok)throw new Error(`fixture request failed (world ${worldResponse.status}, spells ${spellResponse.status}). Run npm run prepare:fixture.`);world=validateWorld(await worldResponse.json());spellFixture=validateSpellFixture(await spellResponse.json());currentRoomId=world.fixture.primary_room_ids[0];renderer.setSize(innerWidth,innerHeight);composer.setSize(innerWidth,innerHeight);buildRoom();requestAnimationFrame(frame);}catch(error){const box=document.querySelector<HTMLElement>("#error")!;box.hidden=false;box.textContent=`Unable to start\n\n${error instanceof Error?error.message:String(error)}`;}}
void boot();
