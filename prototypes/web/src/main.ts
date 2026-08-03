import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import "./style.css";
import { commandDirection, edgesFrom, field, travel, validateWorld, type Edge, type Entity, type Room, type World } from "./model";
import { INITIAL_ROOM_ID, constrainInitialRoomMovement, findInitialRoomTarget, initialRoomCommand, type InitialRoomAction } from "./room3976";
import { findFacingEntity, gameplayCommand, practiceDamage } from "./gameplay";

const canvas = document.querySelector<HTMLCanvasElement>("#world")!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x07090b); scene.fog = new THREE.Fog(0x07090b, 12, 29);
const camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, .05, 80); camera.rotation.order = "YXZ";
const chamber = new THREE.Group(); scene.add(chamber);
const modelLoader = new GLTFLoader();
const loadedModels = new Set<string>();
scene.add(new THREE.HemisphereLight(0x8ba7b5, 0x251a0e, 1.6));
const torch = new THREE.PointLight(0xffb45c, 40, 24); torch.position.set(0, 3.2, 0); torch.castShadow = true; scene.add(torch);

let world: World; let currentRoomId = INITIAL_ROOM_ID; let showHidden = false; let developerVisible = false;
let yaw = 0, pitch = 0, roomGeneration = 0; const keys = new Set<string>(); const exitTriggers: { edge: Edge; position: THREE.Vector3 }[] = [];
const title = document.querySelector<HTMLElement>("#title")!; const description = document.querySelector<HTMLElement>("#description")!;
const exitsElement = document.querySelector<HTMLElement>("#exits")!; const developer = document.querySelector<HTMLElement>("#developer")!;
const interactionPrompt = document.querySelector<HTMLElement>("#interaction-prompt")!; const interactionPanel = document.querySelector<HTMLElement>("#interaction-panel")!;
const interactionTitle = document.querySelector<HTMLElement>("#interaction-title")!; const interactionText = document.querySelector<HTMLElement>("#interaction-text")!;
const tutorial = document.querySelector<HTMLElement>("#tutorial")!; const tutorialProgress = new Set<"look"|"old-man"|"parchment"|"west">();
const playerStatus = document.querySelector<HTMLElement>("#player-status")!;
interface RoomInteraction { id:number; entity: Entity; kind: "npc"|"item"; position: THREE.Vector3; count: number; x:number; z:number }
const roomInteractions: RoomInteraction[]=[]; const inventory=new Set<number>();
let activeEntityId: number|undefined, activeNearbyEntityId:number|undefined; let interactionPinned=false;
let combatTargetId: number|undefined, dummyHealth=30, combatClock=0;

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
    gltf.scene.traverse(object => { if (object instanceof THREE.Mesh) object.castShadow = object.receiveShadow = true; });
    configure?.(gltf.scene);
    chamber.add(gltf.scene);
    loadedModels.add(path);
  } catch (error) {
    console.warn(`Unable to load ${path}; keeping the procedural marker.`, error);
  }
}

function addKnifeModel(position:THREE.Vector3){const group=new THREE.Group();const blade=new THREE.Mesh(new THREE.BoxGeometry(.12,.06,.85),material(0xc7ced0,.3));blade.position.z=-.24;const handle=new THREE.Mesh(new THREE.BoxGeometry(.2,.12,.38),material(0x5b351c,.8));handle.position.z=.37;group.add(blade,handle);group.position.copy(position).setY(.3);group.rotation.y=.55;group.traverse(o=>{if(o instanceof THREE.Mesh)o.castShadow=true;});chamber.add(group);}
function addDummyModel(position:THREE.Vector3){const group=new THREE.Group();const wood=material(0x8a5b2d,.9);const post=new THREE.Mesh(new THREE.CylinderGeometry(.16,.2,2.7,10),wood);post.position.y=1.35;const arms=new THREE.Mesh(new THREE.BoxGeometry(2.1,.18,.18),wood);arms.position.y=1.85;const head=new THREE.Mesh(new THREE.SphereGeometry(.38,10,8),wood);head.position.y=2.75;const base=new THREE.Mesh(new THREE.BoxGeometry(1.5,.16,1.1),wood);base.position.y=.08;group.add(post,arms,head,base);group.position.copy(position).setY(0);group.traverse(o=>{if(o instanceof THREE.Mesh)o.castShadow=true;});chamber.add(group);}

function marker(entity: Entity, kind: "npc"|"item", index: number, generation: number, count: number) {
  const color = kind === "npc" ? 0xa94d3c : 0xc3a44d; const radius = kind === "npc" ? .42 : .25;
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 18, 12), material(color,.55));
  const angle = index * 2.2; const defaultPosition = new THREE.Vector3(Math.cos(angle) * 2.3, radius, Math.sin(angle) * 2.3);
  const knownPosition = entity.id === 3993 ? new THREE.Vector3(2.7, radius, -7.15) : entity.id === 3985 ? new THREE.Vector3(-2.6, 2.05, -8.55) : defaultPosition;
  mesh.position.copy(knownPosition); mesh.castShadow = true; chamber.add(mesh);
  roomInteractions.push({id:entity.id,entity,kind,position:knownPosition.clone(),count,x:knownPosition.x,z:knownPosition.z});
  const label = sprite(`${kind.toUpperCase()} · ${field(entity,"short_description",String(entity.id))}${count>1?` ×${count}`:""}`); label.position.copy(mesh.position).add(new THREE.Vector3(0,1,0)); chamber.add(label);
  if (entity.id === 3993) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(.72,.07,8,32),new THREE.MeshBasicMaterial({color:0xe56b50}));
    ring.rotation.x = Math.PI / 2; ring.position.set(2.7,.04,-7.15); chamber.add(ring);
    mesh.visible = false;
    void addModel("/models/generated/old_man_3993.glb", generation, model => model.position.set(2.7,0,-7.15));
  } else if (entity.id === 3985) {
    mesh.visible = false;
    label.position.set(-2.6,3.25,-8.35);
    void addModel("/models/generated/old_parchment_3985.glb", generation, model => { model.position.set(-2.6,2.05,-8.55); model.rotation.y = Math.PI; });
  } else if(entity.id===72){mesh.visible=false;addKnifeModel(knownPosition);}
  else if(entity.id===3998){mesh.visible=false;addDummyModel(knownPosition);}
}

function sprite(text: string) { const c=document.createElement("canvas"); c.width=512;c.height=64; const x=c.getContext("2d")!; x.fillStyle="#070909cc";x.fillRect(0,0,512,64);x.fillStyle="#eadcae";x.font="25px sans-serif";x.textAlign="center";x.fillText(text.slice(0,38),256,41); const t=new THREE.CanvasTexture(c); const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true}));s.scale.set(4,.5,1);return s; }

function entity(id: number): Entity | undefined { return [...world.npcs,...world.items].find(candidate=>candidate.id===id); }
function cleanDescription(text:string){return text.replace(/\r/g,"\n").replace(/\n\s*\n\s*\d{4,}\s*\n[\s\S]*$/," ").trim();}
function showInteraction(heading: string, text: string, pinned=true) { interactionPinned=pinned;interactionTitle.textContent=heading; interactionText.textContent=cleanDescription(text); interactionPanel.hidden=false; }
function renderPlayerStatus(){playerStatus.textContent=[`INVENTORY · ${inventory.has(72)?"knife":"empty"}`,combatTargetId===3998?`COMBAT · wooden dummy ${dummyHealth}/30 HP`:"COMBAT · peaceful"].join("\n");}
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
  const target=findFacingEntity({x:camera.position.x,z:camera.position.z},{x:forward.x,z:forward.z},roomInteractions);
  if(target)interactEntity(target);else renderUi("Nothing is close enough to interact with.");
}
function interactEntity(target:RoomInteraction){
  if(target.entity.id===3993)return performInitialRoomAction("inspect-old-man");
  if(target.entity.id===3985)return performInitialRoomAction("read-parchment");
  if(target.entity.id===72){inventory.add(72);showInteraction("You take a knife",field(target.entity,"long_description","You take one of the knives."));renderPlayerStatus();return;}
  if(target.entity.id===3998)return startDummyCombat();
  showInteraction(field(target.entity,"short_description",String(target.entity.id)),field(target.entity,"long_description","You see nothing unusual."));
}
function updateInteractionPrompt(forward: THREE.Vector3) {
  const position={x:camera.position.x,z:camera.position.z},direction={x:forward.x,z:forward.z};
  const target=findFacingEntity(position,direction,roomInteractions,9); const nearby=findFacingEntity(position,direction,roomInteractions);
  if(nearby?.entity.id!==activeNearbyEntityId){activeNearbyEntityId=nearby?.entity.id;interactionPrompt.hidden=!nearby;if(nearby){const action=nearby.entity.id===72?"take knife":nearby.entity.id===3998?"attack dummy":"interact";interactionPrompt.textContent=`E · ${action}`;}}
  if(target?.entity.id===activeEntityId)return;
  activeEntityId=target?.entity.id;
  if(target){
    showInteraction(field(target.entity,"short_description",String(target.entity.id)),field(target.entity,"long_description","You see nothing unusual."),false);
  }else if(!interactionPinned)interactionPanel.hidden=true;
}
function startDummyCombat(){if(currentRoomId!==3982)return showInteraction("No target","The wooden practice dummy is not here.");combatTargetId=3998;combatClock=0;showInteraction("Combat started",`You attack the wooden dummy${inventory.has(72)?" with your knife":" with your bare hands"}. Type STOP to disengage.`);renderPlayerStatus();}
function stopCombat(){combatTargetId=undefined;combatClock=0;showInteraction("Combat stopped","You stop attacking.");renderPlayerStatus();}
function advanceCombat(dt:number){if(combatTargetId!==3998)return;combatClock+=dt;if(combatClock<.8)return;combatClock-=.8;const damage=practiceDamage(inventory.has(72));dummyHealth=Math.max(0,dummyHealth-damage);showInteraction("You strike the wooden dummy",`${inventory.has(72)?"Your knife bites into the practice wood":"Your blow thumps against the wood"} for ${damage} damage.\n\nDummy: ${dummyHealth}/30 HP`);if(dummyHealth===0){combatTargetId=undefined;interactionText.textContent+="\n\nThe battered dummy yields. Practice complete.";}renderPlayerStatus();}
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

function buildRoom() {
  const generation = ++roomGeneration; chamber.clear(); exitTriggers.length = 0; roomInteractions.length=0; camera.position.set(0,1.7,0);
  if(currentRoomId!==3982){combatTargetId=undefined;combatClock=0;}else if(dummyHealth<=0)dummyHealth=30;
  if (currentRoomId === 3976) {
    void addModel("/models/generated/training_room_3976.glb", generation);
  } else {
    addBox(new THREE.Vector3(18,.3,18), new THREE.Vector3(0,-.18,0),0x3b3427); addBox(new THREE.Vector3(18,.3,18),new THREE.Vector3(0,5.1,0),0x24272a);
  }
  const visible = edgesFrom(world,currentRoomId,showHidden); const groups = new Map<string,Edge[]>();
  for (const edge of visible) groups.set(edge.direction,[...(groups.get(edge.direction)??[]),edge]);
  for (const [direction, group] of groups) group.forEach((edge,index) => {
    const base=positions[direction] ?? new THREE.Vector3(); const tangent=new THREE.Vector3(-base.z,0,base.x).normalize(); const at=base.clone().addScaledVector(tangent,(index-(group.length-1)/2)*1.7);
    if (currentRoomId === 3976 && direction === "W") {
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
  for (const entry of roomSpawn?.entries??[]) { const list=entry.entity_type==="npc"?world.npcs:world.items; const e=list.find(x=>x.id===entry.entity_id); if(e) marker(e,entry.entity_type,markerIndex++,generation,entry.count); }
  interactionPanel.hidden=true; interactionPinned=false; activeEntityId=undefined; activeNearbyEntityId=undefined; interactionPrompt.hidden=true; renderUi(); renderTutorial(); renderPlayerStatus();
}

function renderUi(message="") {
  const room=world.rooms.find(r=>r.id===currentRoomId)!; const all=world.edges.filter(e=>e.from_room===currentRoomId); const visible=edgesFrom(world,currentRoomId,showHidden);
  title.textContent=`${field(room,"short_description",room.scope==="stub"?"Boundary room":"Untitled room")}  [${room.id}]`;
  description.textContent=field(room,"long_description",room.scope==="stub"?"This is a skeletal boundary stub. Travel can continue only along exported authoritative edges.":"No description was decoded.");
  exitsElement.textContent=`Exits: ${visible.map(e=>`${e.direction}→${e.to_room}${e.door?" [door]":""}${e.hidden?" [hidden]":""}`).join(" · ") || "none"}${message?`  — ${message}`:""}`;
  developer.hidden=!developerVisible; developer.textContent=[`room ${room.stable_id}`,`scope ${room.scope}`,`region ${room.display?.region??"unknown"} (${room.display?.region_name??"unknown"})`,`source row ${room.provenance?.source_row_id??"unknown"}`,`edges ${visible.length} visible / ${all.length} total`,`parallel directions ${[...new Set(all.filter((e,i,a)=>a.findIndex(x=>x.direction===e.direction)!==i).map(e=>e.direction))].join(", ")||"none"}`,`hidden ${showHidden?"shown":"suppressed"}`,`fixture ${world.fixture.id}`,`contract ${world.contract.name} ${world.contract.version}`].join("\n");
}

function go(edge: Edge) { if(currentRoomId===INITIAL_ROOM_ID&&edge.direction==="W")tutorialProgress.add("west"); currentRoomId=edge.to_room; buildRoom(); }
function issue(raw: string) {
  const c=raw.trim().toLowerCase(); if(!c)return;
  if(currentRoomId===INITIAL_ROOM_ID&&(c==="diagnose"||c==="test room"))return runInitialRoomDiagnostics();
  const initialAction=currentRoomId===INITIAL_ROOM_ID?initialRoomCommand(c):undefined;
  if(initialAction)return performInitialRoomAction(initialAction);
  const action=gameplayCommand(c);
  if(action==="get-knife"){
    if(currentRoomId!==3980)return showInteraction("No knife here","You do not see a knife close enough to take.");
    inventory.add(72);showInteraction("You take a knife",field(entity(72)!,"long_description","You take one of the knives."));renderPlayerStatus();return;
  }
  if(action==="attack-dummy")return startDummyCombat();
  if(action==="stop-combat")return stopCombat();
  if(action==="inventory")return showInteraction("Inventory",inventory.has(72)?"knife":"You are carrying nothing.");
  if(c==="look"||c==="l")return renderUi("You look around.");
  const edge=travel(world,currentRoomId,c,showHidden); if(edge)return go(edge);
  renderUi(commandDirection(c)?"No such visible exit.":`Unknown command: ${raw}`);
}

document.querySelector<HTMLFormElement>("#command-form")!.addEventListener("submit",event=>{event.preventDefault();const input=document.querySelector<HTMLInputElement>("#command")!;issue(input.value);input.value="";});
canvas.addEventListener("click",()=>canvas.requestPointerLock()); document.addEventListener("mousemove",e=>{if(document.pointerLockElement!==canvas)return;yaw-=e.movementX*.002;pitch=Math.max(-1.35,Math.min(1.35,pitch-e.movementY*.002));});
addEventListener("keydown",e=>{if((e.target as HTMLElement).tagName==="INPUT")return;keys.add(e.code);if(e.code==="KeyE"&&!e.repeat)interactNearby();if(e.key.toLowerCase()==="h"){showHidden=!showHidden;buildRoom();}if(e.key==="`"){developerVisible=!developerVisible;renderUi();}});addEventListener("keyup",e=>keys.delete(e.code));
addEventListener("resize",()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});

let last=performance.now(), transitionCooldown=0;
function frame(now:number){requestAnimationFrame(frame);const dt=Math.min((now-last)/1000,.05);last=now;camera.rotation.set(pitch,yaw,0);const forward=new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(0,yaw,0));const right=new THREE.Vector3(1,0,0).applyEuler(new THREE.Euler(0,yaw,0));const proposed=camera.position.clone();if(keys.has("KeyW"))proposed.addScaledVector(forward,dt*4);if(keys.has("KeyS"))proposed.addScaledVector(forward,-dt*4);if(keys.has("KeyA"))proposed.addScaledVector(right,-dt*4);if(keys.has("KeyD"))proposed.addScaledVector(right,dt*4);if(currentRoomId===INITIAL_ROOM_ID){const constrained=constrainInitialRoomMovement({x:proposed.x,z:proposed.z});camera.position.set(constrained.x,1.7,constrained.z);}else{camera.position.set(THREE.MathUtils.clamp(proposed.x,-8.5,8.5),1.7,THREE.MathUtils.clamp(proposed.z,-8.5,8.5));}updateInteractionPrompt(forward);advanceCombat(dt);transitionCooldown-=dt;if(transitionCooldown<=0){const hit=exitTriggers.find(x=>x.position.distanceTo(camera.position.clone().setY(0))<1.05);if(hit){transitionCooldown=1;go(hit.edge);}}renderer.render(scene,camera);}

async function boot(){try{const response=await fetch("/private/pendelhaven-v1.json",{cache:"no-store"});if(!response.ok)throw new Error(`fixture request failed (${response.status}). Run npm run prepare:fixture or the documented PowerShell command.`);world=validateWorld(await response.json());currentRoomId=world.fixture.primary_room_ids[0];renderer.setSize(innerWidth,innerHeight);buildRoom();requestAnimationFrame(frame);}catch(error){const box=document.querySelector<HTMLElement>("#error")!;box.hidden=false;box.textContent=`Unable to start\n\n${error instanceof Error?error.message:String(error)}`;}}
void boot();
