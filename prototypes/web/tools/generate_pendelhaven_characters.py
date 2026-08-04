"""Generate description-driven GLBs for central Pendelhaven NPCs and arena creatures."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from generate_initial_room_models import ROOT,clear,cube,cylinder,export_glb,material,sphere

PREVIEW=ROOT/"var"/"previews"/"pendelhaven-characters.png"

def block(name,location,scale,mat,rotation=(0,0,0),bevel=.06):
    obj=cube(name,location,scale,mat,bevel);obj.rotation_euler=rotation;return obj

def palette():
    return {
        "skin":material("Natural skin",(.48,.29,.18,1),roughness=.78),"tan":material("Deep tanned skin",(.34,.18,.09,1),roughness=.8),
        "pale":material("Pale skin",(.62,.45,.35,1),roughness=.78),"dark":material("Deep skin",(.22,.12,.075,1),roughness=.8),
        "black":material("Black hair",(.025,.018,.014,1),roughness=.9),"brown":material("Brown hair",(.11,.052,.024,1),roughness=.9),
        "red":material("Copper red hair",(.48,.095,.025,1),roughness=.86),"blonde":material("Golden blonde hair",(.68,.46,.16,1),roughness=.84),
        "boot":material("Worn leather boots",(.07,.035,.017,1),roughness=.88),"eye":material("Dark pupils",(.012,.012,.01,1),roughness=.28),
        "steel":material("Tempered steel",(.52,.57,.58,1),metallic=.82,roughness=.22),"wood":material("Weapon wood",(.26,.11,.035,1),roughness=.84),
    }

def humanoid(m,skin,top,bottom,hair="black",height=1.0,broad=1.0,robe=False,hood=False):
    leg_y=.66*height;torso_y=1.72*height;head_y=2.7*height
    if robe:block("Layered robe",(0,.88*height,0),(.9*broad,1.76*height,.66),bottom,bevel=.13)
    else:
        for x in (-.22*broad,.22*broad):block("Booted leg",(x,leg_y,0),(.3*broad,1.25*height,.36),m["boot"],bevel=.1)
    block("Fitted torso",(0,torso_y,0),(.82*broad,1.18*height,.58),top,bevel=.16)
    for x,angle in ((-.52*broad,-.04),(.52*broad,.04)):block("Detailed arm",(x,1.68*height,.02),(.24*broad,1.12*height,.26),top,(0,0,angle),.1)
    sphere("Head",(0,head_y,.03),(.36*broad,.43*height,.35),m[skin]);block("Hair",(0,2.96*height,-.03),(.72*broad,.28*height,.64),m[hair],bevel=.15)
    for x in (-.13*broad,.13*broad):sphere("Eye",(x,2.75*height,.34),(.038,.045,.025),m["eye"])
    if hood:block("Deep hood",(0,2.75*height,-.08),(.9*broad,.9*height,.7),top,bevel=.2)
    return head_y

def big_ed():
    clear();m=palette();smock=material("Grease-stained yellow smock",(.52,.39,.12,1),roughness=.96);shirt=material("Loose tavern shirt",(.28,.18,.11,1),roughness=.92);ale=material("Ale stain",(.22,.09,.02,1),roughness=1)
    humanoid(m,"skin",shirt,m["boot"],hair="brown",height=1.08,broad=1.48);block("Huge stained smock",(0,1.62,.34),(1.35,1.55,.14),smock,bevel=.12)
    for x,y in ((-.25,1.7),(.3,1.25),(.12,2.05)):sphere("Old grease stain",(x,y,.43),(.13,.09,.025),ale)
    block("Heavy beard",(0,2.68,.34),(.5,.45,.18),m["brown"],bevel=.13)
    return export_glb("big_ed_4175.glb")

def rhune():
    clear();m=palette();leather=material("Dark green studded leather",(.035,.21,.095,1),roughness=.72);stud=material("Jerkin studs",(.47,.5,.45,1),metallic=.7,roughness=.32);coin=material("Counted coins",(.72,.48,.1,1),metallic=.72,roughness=.26)
    humanoid(m,"pale",leather,leather,hair="brown",height=.96,broad=.82);block("Fitted leather jerkin",(0,1.72,.31),(.7,1.0,.12),leather,bevel=.1)
    for x in (-.27,0,.27):
        for y in (1.45,1.72,1.99):sphere("Silver jerkin stud",(x,y,.39),(.035,.035,.025),stud)
    for x in (-.42,.42):block("Pointed elven ear",(x,2.68,.03),(.24,.11,.08),m["pale"],(0,0,.25 if x>0 else -.25),.04)
    for x in (-.16,0,.16):cylinder("Coin",(x,1.18,.5),.1,.035,coin,vertices=20)
    return export_glb("rhune_4176.glb")

def ooteeny():
    clear();m=palette();cloak=material("Collector hooded cloak",(.12,.105,.095,1),roughness=.97);bag=material("Overfilled appraisal satchel",(.28,.16,.065,1),roughness=.9)
    humanoid(m,"dark",cloak,cloak,hair="black",height=.78,broad=.88,robe=True,hood=True);sphere("Collector satchel",(.62,.92,-.02),(.42,.58,.3),bag);block("Satchel strap",(.25,1.55,.25),(.12,1.5,.08),bag,(0,0,-.42),.03)
    return export_glb("ooteeny_4177.glb")

def ezekiel():
    clear();m=palette();tunic=material("Pendelhaven shop tunic",(.28,.24,.17,1),roughness=.9);apron=material("General store apron",(.38,.3,.18,1),roughness=.96);blue=material("Piercing blue eyes",(.035,.24,.72,1),roughness=.2)
    humanoid(m,"skin",tunic,m["boot"],height=1.0,broad=.98);block("Work apron",(0,1.55,.34),(.68,1.45,.1),apron,bevel=.08)
    for x in (-.13,.13):sphere("Blue eye",(x,2.75,.36),(.045,.05,.026),blue)
    return export_glb("ezekiel_4178.glb")

def issac():
    clear();m=palette();armor=material("Armorer leather vest",(.26,.11,.045,1),roughness=.75);green=material("Bright green eyes",(.08,.62,.18,1),roughness=.18);thread=material("Seamstress thread",(.7,.53,.2,1),roughness=.8)
    humanoid(m,"tan",armor,m["boot"],hair="red",height=1.02,broad=1.03);block("Shoulder-length red hair",(0,2.62,-.22),(.75,.85,.3),m["red"],bevel=.16)
    for x in (-.13,.13):sphere("Green eye",(x,2.8,.35),(.045,.05,.025),green)
    cylinder("Leather awl",(.52,1.12,.32),.04,.65,m["steel"],rotation=(.5,0,0),vertices=12);sphere("Thread spool",(-.45,1.16,.34),(.16,.18,.13),thread)
    return export_glb("issac_4179.glb")

def davis():
    clear();m=palette();tunic=material("Weaponsmith tunic",(.22,.19,.14,1),roughness=.86);belt=material("Broad weapons belt",(.13,.055,.02,1),roughness=.82)
    humanoid(m,"skin",tunic,m["boot"],hair="blonde",height=1.06,broad=1.25);block("Tied blonde ponytail",(0,2.72,-.42),(.24,.78,.24),m["blonde"],bevel=.12);block("Broad weapon belt",(0,1.25,.02),(1.05,.22,.7),belt,bevel=.06)
    block("Demonstration sword",(.72,1.45,.25),(.1,1.65,.09),m["steel"],(0,0,-.48),.025);block("Sword grip",(.27,.82,.25),(.18,.46,.16),m["wood"],(0,0,-.48),.04)
    return export_glb("davis_4180.glb")

def vivian():
    clear();m=palette();robe=material("Myias white robes",(.72,.7,.67,1),roughness=.9);purple=material("Myias purple stole",(.34,.095,.48,1),roughness=.8);holy=material("Life holy symbol",(.72,.55,.18,1),metallic=.62,roughness=.26);aura=material("Protective magick aura",(.4,.25,.75,.22),roughness=.18,emission=(.22,.1,.55,1))
    humanoid(m,"pale",robe,robe,hair="black",height=1.0,broad=.94,robe=True);block("Purple healer stole",(0,1.75,.36),(.34,1.7,.1),purple,bevel=.06)
    for y,radius in ((.65,.72),(1.45,.85),(2.3,.68)):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.025,major_segments=32,minor_segments=7,location=(0,y,0));aura_ring=bpy.context.object;aura_ring.name="Shimmering protective aura";aura_ring.data.materials.append(aura)
    torus_obj=None;bpy.ops.mesh.primitive_torus_add(major_radius=.23,minor_radius=.055,major_segments=24,minor_segments=8,location=(0,1.85,.48),rotation=(math.pi/2,0,0));torus_obj=bpy.context.object;torus_obj.name="Life holy symbol";torus_obj.data.materials.append(holy)
    return export_glb("vivian_4181.glb")

def oscar():
    clear();m=palette();guild=material("Guildmaster armor",(.25,.16,.08,1),roughness=.72);plate=material("Guild plate",(.33,.36,.35,1),metallic=.7,roughness=.35);gold=material("Golden eyes",(.88,.62,.09,1),roughness=.16)
    humanoid(m,"tan",guild,m["boot"],hair="black",height=1.1,broad=1.34);block("Guild breastplate",(0,1.85,.32),(1.02,1.15,.16),plate,bevel=.14)
    for x in (-.13,.13):sphere("Golden eye",(x,3.02,.36),(.05,.055,.025),gold)
    block("Guildmaster bracer",(-.67,1.5,.1),(.32,.65,.34),plate,bevel=.08);block("Guildmaster bracer",(.67,1.5,.1),(.32,.65,.34),plate,bevel=.08)
    return export_glb("oscar_4182.glb")

def slug():
    clear();body=material("Wet gray slug hide",(.28,.3,.29,1),roughness=.28);belly=material("Pale slug foot",(.43,.41,.34,1),roughness=.38);slime=material("Translucent slime trail",(.23,.45,.42,.35),roughness=.16);eye=material("Slug eye",(.012,.012,.01,1),roughness=.2)
    sphere("Four-foot slug body",(0,.48,0),(.72,.55,1.85),body);sphere("Slug mantle",(0,.72,-.35),(.68,.65,.8),body);block("Slimy foot",(0,.16,.2),(1.25,.16,3.4),belly,bevel=.22);block("Slime trail",(0,.035,1.65),(1.05,.04,2.4),slime,bevel=.22)
    for x in (-.34,.34):block("Eye stalk",(x,1.05,-1.35),(.09,.75,.09),body,(.3,0,0),.04);sphere("Slug eye",(x,1.42,-1.5),(.11,.11,.11),eye)
    return export_glb("giant_slug_4003.glb")

def kobold_variant(filename,large=False,thug=False,guard=False):
    clear();m=palette();scale=1.12 if guard else 1.0;skin=material("Dry brown kobold scales",(.27,.16,.075,1),roughness=.96);belly=material("Kobold belly scales",(.43,.29,.13,1),roughness=.92);cloth=material("Filthy kobold wraps",(.21,.16,.09,1),roughness=1);leather=material("Kobold scrap leather",(.18,.075,.028,1),roughness=.86);red=material("Kobold anxious eyes",(.65,.08,.03,1),roughness=.2)
    for x in (-.2,.2):block("Clawed leg",(x,.5*scale,.05),(.27,1.0*scale,.36),skin,bevel=.1)
    block("Scaled kobold torso",(0,1.35*scale,0),((.82 if thug or guard else .7),1.25*scale,.58),skin,bevel=.18);block("Belly scales",(0,1.35*scale,.32),(.45,.85*scale,.08),belly,bevel=.08)
    for x,a in ((-.48,-.1),(.48,.1)):block("Kobold arm",(x,1.33*scale,.02),(.22,1.05*scale,.24),skin,(0,0,a),.09)
    sphere("Head",(0,2.2*scale,.03),(.42,.42*scale,.42),skin);block("Dog-like muzzle",(0,2.12*scale,.43),(.52,.28,.55),skin,bevel=.14)
    for x in (-.37,.37):block("Perked pointed ear",(x,2.46*scale,-.02),(.42,.52,.12),skin,(0,0,.55 if x>0 else -.55),.08);sphere("Kobold eye",(x*.42,2.29*scale,.4),(.055,.06,.03),red)
    block("Rag waist wrap",(0,.96*scale,.03),(.84,.35,.62),cloth,bevel=.07)
    if thug:block("Thug leather harness",(0,1.48*scale,.3),(.72,.82,.12),leather,bevel=.08)
    if guard:
        block("Guard scrap breastplate",(0,1.55*scale,.32),(.82,.86,.15),m["steel"],bevel=.1);block("Hammer haft",(.72,1.25,.05),(.13,2.25,.13),m["wood"],(0,0,-.25),.035);block("Heavy hammer head",(.94,2.25,.05),(.82,.4,.42),m["steel"],(0,0,-.25),.08)
    elif thug:block("Thug cudgel",(.65,1.2,.1),(.2,1.6,.22),m["wood"],(0,0,-.38),.08)
    else:block("Kobold dagger",(.62,1.28,.32),(.09,1.05,.07),m["steel"],(0,0,-.5),.02)
    return export_glb(filename)

def render_preview(paths):
    clear();offsets=[(-9,5),(-5.5,5),(-2,5),(2,5),(5.5,5),(9,5),(-9,0),(-5.5,0),(-2,0),(2,0),(5.5,0),(9,0)]
    for path,(x,y) in zip(paths,offsets):
        bpy.ops.import_scene.gltf(filepath=str(path));imported=list(bpy.context.selected_objects)
        for obj in imported:obj.location+=Vector((x,y,0))
    cube("Character preview floor",(0,2.5,-.12),(24,10,.2),material("Preview stone",(.08,.085,.09,1),roughness=.95),.04)
    bpy.ops.object.camera_add(location=(15,-28,12));camera=bpy.context.object;camera.data.lens=55;camera.rotation_euler=(Vector((0,2.5,1.3))-camera.location).to_track_quat("-Z","Y").to_euler();bpy.context.scene.camera=camera
    bpy.ops.object.light_add(type="AREA",location=(-7,-8,13));bpy.context.object.data.energy=2600;bpy.context.object.data.size=11
    bpy.ops.object.light_add(type="AREA",location=(10,4,8));bpy.context.object.data.energy=1300;bpy.context.object.data.color=(1,.58,.34);bpy.context.object.data.size=9
    scene=bpy.context.scene;scene.render.engine="BLENDER_EEVEE";scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG";PREVIEW.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(PREVIEW);scene.world.color=(.01,.012,.016);bpy.ops.render.render(write_still=True)

def main():
    paths=[big_ed(),rhune(),ooteeny(),ezekiel(),issac(),davis(),vivian(),oscar(),slug(),kobold_variant("kobold_129.glb"),kobold_variant("kobold_thug_4004.glb",thug=True),kobold_variant("kobold_guard_4006.glb",large=True,guard=True)]
    render_preview(paths);print("Generated Pendelhaven characters:",*(str(path) for path in paths),str(PREVIEW),sep="\n")

if __name__=="__main__":main()
