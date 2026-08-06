import * as THREE from "three";
import type {EquipmentId,PlayerClass,PlayerRace} from "./rpg";

export interface PlayerAvatar {root:THREE.Group;leftArm:THREE.Group;rightArm:THREE.Group;leftLeg:THREE.Group;rightLeg:THREE.Group;weaponAnchor:THREE.Group;baseScale:number}

function standard(color:number,metalness=0,roughness=.72){return new THREE.MeshStandardMaterial({color,metalness,roughness});}
function mesh(geometry:THREE.BufferGeometry,material:THREE.Material){const value=new THREE.Mesh(geometry,material);value.castShadow=value.receiveShadow=true;return value;}

export function createPlayerAvatar(race:PlayerRace,playerClass:PlayerClass):PlayerAvatar{
  const root=new THREE.Group();root.name="Player avatar";
  const raceScale=race==="Dwarf"?.82:race==="Gnome"?.72:race==="Giant"?1.28:race==="Fairfolk"?.88:1;const width=race==="Dwarf"?1.22:race==="Gnome"?.82:race==="Giant"?1.18:race==="Fairfolk"?.84:1;
  const classColor:Record<PlayerClass,number>={Warrior:0x53616b,Scholar:0x6b583a,Gypsy:0x244c35,Priest:0xd5ccb4,Mage:0x4b3571,Archtypical:0x665747};
  const skinColor=race==="Elf"?0xc99778:race==="Dwarf"?0x9a684c:race==="Gnome"?0xb6815e:race==="Giant"?0x936247:race==="Fairfolk"?0xd0a184:0xad7658;
  const cloth=standard(classColor[playerClass],playerClass==="Warrior"?.52:.05,playerClass==="Warrior"?.38:.72);const skin=standard(skinColor,0,.78);const leather=standard(0x2d170d,0,.82);const metal=standard(0x7d8586,.75,.28);
  const hips=new THREE.Group();hips.position.y=.92;root.add(hips);
  const torso=mesh(new THREE.CapsuleGeometry(.38*width,.68,8,16),cloth);torso.position.y=1.7;torso.scale.z=.72;root.add(torso);
  const belt=mesh(new THREE.TorusGeometry(.39*width,.055,8,24),leather);belt.rotation.x=Math.PI/2;belt.position.y=1.28;root.add(belt);
  const head=mesh(new THREE.SphereGeometry(.3*width,24,16),skin);head.position.set(0,2.55,.02);root.add(head);
  const hair=mesh(new THREE.SphereGeometry(.305*width,20,10,0,Math.PI*2,0,Math.PI*.52),standard(race==="Dwarf"?0x4b2513:0x25160f));hair.position.set(0,2.61,.01);root.add(hair);
  for(const x of [-.105,.105]){const eye=mesh(new THREE.SphereGeometry(.027,10,7),standard(0x19394e,0,.25));eye.position.set(x,2.59,-.285);root.add(eye);}
  if(race==="Elf"||race==="Fairfolk")for(const x of [-1,1]){const ear=mesh(new THREE.ConeGeometry(.1,.34,10),skin);ear.position.set(x*.34,2.57,0);ear.rotation.z=x*-Math.PI/2;root.add(ear);}
  if(race==="Fairfolk")for(const x of [-1,1]){const wing=mesh(new THREE.CircleGeometry(.42,18),standard(0x95c9c6,0,.28));wing.material.transparent=true;wing.material.opacity=.62;wing.position.set(x*.35,1.75,.25);wing.rotation.y=x*.5;root.add(wing);}
  if(race==="Dwarf"){const beard=mesh(new THREE.ConeGeometry(.3,.75,16),standard(0x5a2d17));beard.position.set(0,2.18,-.18);beard.rotation.x=Math.PI;root.add(beard);}
  function limb(x:number,y:number,isArm:boolean){const pivot=new THREE.Group();pivot.position.set(x,y,0);const part=mesh(new THREE.CapsuleGeometry(isArm?.105:.135,isArm?.58:.7,7,12),isArm?cloth:leather);part.position.y=-(isArm?.35:.43);pivot.add(part);return pivot;}
  const leftArm=limb(-.48*width,2.05,true),rightArm=limb(.48*width,2.05,true),leftLeg=limb(-.2*width,1.08,false),rightLeg=limb(.2*width,1.08,false);root.add(leftArm,rightArm,leftLeg,rightLeg);
  const weaponAnchor=new THREE.Group();weaponAnchor.position.set(0,-.7,-.02);rightArm.add(weaponAnchor);
  if(playerClass==="Warrior"){for(const x of [-.48,.48]){const pauldron=mesh(new THREE.SphereGeometry(.18,14,9),metal);pauldron.scale.y=.65;pauldron.position.set(x*width,2.08,0);root.add(pauldron);}}
  if(playerClass==="Mage"){const hood=mesh(new THREE.ConeGeometry(.42,.72,20),cloth);hood.position.set(0,2.85,.05);root.add(hood);}
  root.scale.set(width,raceScale,width);return {root,leftArm,rightArm,leftLeg,rightLeg,weaponAnchor,baseScale:raceScale};
}

export function setAvatarEquipment(avatar:PlayerAvatar,equipment?:EquipmentId){avatar.weaponAnchor.clear();if(!equipment)return;const metal=standard(0x9ca5a6,.82,.22),wood=standard(0x3c1d0c,0,.84);if(equipment==="guard-hammer"){const haft=mesh(new THREE.CylinderGeometry(.045,.055,1.5,12),wood);haft.position.y=-.55;const head=mesh(new THREE.BoxGeometry(.62,.26,.28),metal);head.position.y=-1.25;avatar.weaponAnchor.add(haft,head);}else{const blade=mesh(new THREE.BoxGeometry(.11,equipment==="kobold-dagger"?.85:.62,.055),metal);blade.position.y=-.48;const grip=mesh(new THREE.CylinderGeometry(.065,.065,.34,10),wood);grip.position.y=.08;avatar.weaponAnchor.add(blade,grip);}}

export function animatePlayerAvatar(avatar:PlayerAvatar,time:number,moving:boolean,running:boolean,attacking:boolean){const speed=running?12:7,amplitude=running?.9:.55,cycle=Math.sin(time*speed);const target=moving?cycle*amplitude:0;avatar.leftLeg.rotation.x=THREE.MathUtils.lerp(avatar.leftLeg.rotation.x,target,.22);avatar.rightLeg.rotation.x=THREE.MathUtils.lerp(avatar.rightLeg.rotation.x,-target,.22);avatar.leftArm.rotation.x=THREE.MathUtils.lerp(avatar.leftArm.rotation.x,-target*.75,.22);avatar.rightArm.rotation.x=THREE.MathUtils.lerp(avatar.rightArm.rotation.x,attacking?-1.6+Math.sin(time*18)*.65:target*.75,.3);avatar.root.position.y=moving?Math.abs(Math.sin(time*speed))* (running?.08:.035):0;}
