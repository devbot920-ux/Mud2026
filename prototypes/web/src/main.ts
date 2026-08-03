import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import "./style.css";
import { commandDirection, edgesFrom, field, travel, validateWorld, type Edge, type Entity, type Room, type World } from "./model";

const canvas = document.querySelector<HTMLCanvasElement>("#world")!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x07090b); scene.fog = new THREE.Fog(0x07090b, 12, 29);
const camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, .05, 80); camera.rotation.order = "YXZ";
const chamber = new THREE.Group(); scene.add(chamber);
const modelLoader = new GLTFLoader();
scene.add(new THREE.HemisphereLight(0x8ba7b5, 0x251a0e, 1.6));
const torch = new THREE.PointLight(0xffb45c, 40, 24); torch.position.set(0, 3.2, 0); torch.castShadow = true; scene.add(torch);

let world: World; let currentRoomId = 3976; let showHidden = false; let developerVisible = true;
let yaw = 0, pitch = 0, roomGeneration = 0; const keys = new Set<string>(); const exitTriggers: { edge: Edge; position: THREE.Vector3 }[] = [];
const title = document.querySelector<HTMLElement>("#title")!; const description = document.querySelector<HTMLElement>("#description")!;
const exitsElement = document.querySelector<HTMLElement>("#exits")!; const developer = document.querySelector<HTMLElement>("#developer")!;

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
  } catch (error) {
    console.warn(`Unable to load ${path}; keeping the procedural marker.`, error);
  }
}

function marker(entity: Entity, kind: "npc"|"item", index: number, generation: number) {
  const color = kind === "npc" ? 0xa94d3c : 0xc3a44d; const radius = kind === "npc" ? .42 : .25;
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 18, 12), material(color,.55));
  const angle = index * 2.2; const defaultPosition = new THREE.Vector3(Math.cos(angle) * 2.3, radius, Math.sin(angle) * 2.3);
  const knownPosition = entity.id === 3993 ? new THREE.Vector3(2.7, radius, -7.15) : entity.id === 3985 ? new THREE.Vector3(-2.6, 2.05, -8.55) : defaultPosition;
  mesh.position.copy(knownPosition); mesh.castShadow = true; chamber.add(mesh);
  const label = sprite(`${kind.toUpperCase()} · ${field(entity,"short_description",String(entity.id))}`); label.position.copy(mesh.position).add(new THREE.Vector3(0,1,0)); chamber.add(label);
  if (entity.id === 3993) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(.72,.07,8,32),new THREE.MeshBasicMaterial({color:0xe56b50}));
    ring.rotation.x = Math.PI / 2; ring.position.set(2.7,.04,-7.15); chamber.add(ring);
    mesh.visible = false;
    void addModel("/models/generated/old_man_3993.glb", generation, model => model.position.set(2.7,0,-7.15));
  } else if (entity.id === 3985) {
    mesh.visible = false;
    label.position.set(-2.6,3.25,-8.35);
    void addModel("/models/generated/old_parchment_3985.glb", generation, model => { model.position.set(-2.6,2.05,-8.55); model.rotation.y = Math.PI; });
  }
}

function sprite(text: string) { const c=document.createElement("canvas"); c.width=512;c.height=64; const x=c.getContext("2d")!; x.fillStyle="#070909cc";x.fillRect(0,0,512,64);x.fillStyle="#eadcae";x.font="25px sans-serif";x.textAlign="center";x.fillText(text.slice(0,38),256,41); const t=new THREE.CanvasTexture(c); const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true}));s.scale.set(4,.5,1);return s; }

function buildRoom() {
  const generation = ++roomGeneration; chamber.clear(); exitTriggers.length = 0; camera.position.set(0,1.7,0);
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
  for (const entry of roomSpawn?.entries??[]) { const list=entry.entity_type==="npc"?world.npcs:world.items; const e=list.find(x=>x.id===entry.entity_id); if(e) marker(e,entry.entity_type,markerIndex++,generation); }
  renderUi();
}

function renderUi(message="") {
  const room=world.rooms.find(r=>r.id===currentRoomId)!; const all=world.edges.filter(e=>e.from_room===currentRoomId); const visible=edgesFrom(world,currentRoomId,showHidden);
  title.textContent=`${field(room,"short_description",room.scope==="stub"?"Boundary room":"Untitled room")}  [${room.id}]`;
  description.textContent=field(room,"long_description",room.scope==="stub"?"This is a skeletal boundary stub. Travel can continue only along exported authoritative edges.":"No description was decoded.");
  exitsElement.textContent=`Exits: ${visible.map(e=>`${e.direction}→${e.to_room}${e.door?" [door]":""}${e.hidden?" [hidden]":""}`).join(" · ") || "none"}${message?`  — ${message}`:""}`;
  developer.hidden=!developerVisible; developer.textContent=[`room ${room.stable_id}`,`scope ${room.scope}`,`region ${room.display?.region??"unknown"} (${room.display?.region_name??"unknown"})`,`source row ${room.provenance?.source_row_id??"unknown"}`,`edges ${visible.length} visible / ${all.length} total`,`parallel directions ${[...new Set(all.filter((e,i,a)=>a.findIndex(x=>x.direction===e.direction)!==i).map(e=>e.direction))].join(", ")||"none"}`,`hidden ${showHidden?"shown":"suppressed"}`,`fixture ${world.fixture.id}`,`contract ${world.contract.name} ${world.contract.version}`].join("\n");
}

function go(edge: Edge) { currentRoomId=edge.to_room; buildRoom(); }
function issue(raw: string) { const c=raw.trim().toLowerCase(); if(!c)return; if(c==="look"||c==="l")return renderUi("You look around."); const edge=travel(world,currentRoomId,c,showHidden); if(edge)return go(edge); renderUi(commandDirection(c)?"No such visible exit.":`Unknown command: ${raw}`); }

document.querySelector<HTMLFormElement>("#command-form")!.addEventListener("submit",event=>{event.preventDefault();const input=document.querySelector<HTMLInputElement>("#command")!;issue(input.value);input.value="";});
canvas.addEventListener("click",()=>canvas.requestPointerLock()); document.addEventListener("mousemove",e=>{if(document.pointerLockElement!==canvas)return;yaw-=e.movementX*.002;pitch=Math.max(-1.35,Math.min(1.35,pitch-e.movementY*.002));});
addEventListener("keydown",e=>{if((e.target as HTMLElement).tagName==="INPUT")return;keys.add(e.code);if(e.key.toLowerCase()==="h"){showHidden=!showHidden;buildRoom();}if(e.key==="`"){developerVisible=!developerVisible;renderUi();}});addEventListener("keyup",e=>keys.delete(e.code));
addEventListener("resize",()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});

let last=performance.now(), transitionCooldown=0;
function frame(now:number){requestAnimationFrame(frame);const dt=Math.min((now-last)/1000,.05);last=now;camera.rotation.set(pitch,yaw,0);const forward=new THREE.Vector3(0,0,-1).applyEuler(new THREE.Euler(0,yaw,0));const right=new THREE.Vector3(1,0,0).applyEuler(new THREE.Euler(0,yaw,0));if(keys.has("KeyW"))camera.position.addScaledVector(forward,dt*4);if(keys.has("KeyS"))camera.position.addScaledVector(forward,-dt*4);if(keys.has("KeyA"))camera.position.addScaledVector(right,-dt*4);if(keys.has("KeyD"))camera.position.addScaledVector(right,dt*4);camera.position.y=1.7;camera.position.x=THREE.MathUtils.clamp(camera.position.x,-8.5,8.5);camera.position.z=THREE.MathUtils.clamp(camera.position.z,-8.5,8.5);transitionCooldown-=dt;if(transitionCooldown<=0){const hit=exitTriggers.find(x=>x.position.distanceTo(camera.position.clone().setY(0))<1.05);if(hit){transitionCooldown=1;go(hit.edge);}}renderer.render(scene,camera);}

async function boot(){try{const response=await fetch("/private/pendelhaven-v1.json",{cache:"no-store"});if(!response.ok)throw new Error(`fixture request failed (${response.status}). Run npm run prepare:fixture or the documented PowerShell command.`);world=validateWorld(await response.json());currentRoomId=world.fixture.primary_room_ids[0];renderer.setSize(innerWidth,innerHeight);buildRoom();requestAnimationFrame(frame);}catch(error){const box=document.querySelector<HTMLElement>("#error")!;box.hidden=false;box.textContent=`Unable to start\n\n${error instanceof Error?error.message:String(error)}`;}}
void boot();
