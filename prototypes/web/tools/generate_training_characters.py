"""Generate full-body stylized character GLBs for tutorial NPCs 3993-3998."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_initial_room_models import ROOT, clear, cube, export_glb, material, sphere


PREVIEW = ROOT / "var" / "previews" / "training-characters.png"


def block(name, location, scale, mat, rotation=(0, 0, 0), bevel=.04):
    obj=cube(name,location,scale,mat,bevel);obj.rotation_euler=rotation;return obj


def common_materials():
    return {
        "skin":material("Warm stylized skin",(.53,.34,.23,1),roughness=.88),
        "dark_skin":material("Deep stylized skin",(.28,.16,.105,1),roughness=.88),
        "hair":material("Dark hair",(.065,.042,.027,1),roughness=.96),
        "gray":material("Gray hair",(.31,.32,.30,1),roughness=.96),
        "boot":material("Leather footwear",(.055,.035,.022,1),roughness=.9),
        "eye":material("Eyes",(.025,.02,.016,1),roughness=.5),
    }


def face(mats, skin="skin", hair="hair", bun=False):
    sphere("Head",(0,2.72,.02),(.36,.43,.34),mats[skin]);block("Hair cap",(0,2.95,-.03),(.7,.28,.62),mats[hair],bevel=.12)
    for x in (-.13,.13): sphere("Eye",(x,2.77,.33),(.035,.045,.025),mats["eye"])
    if bun:sphere("Hair bun",(0,2.92,-.37),(.24,.24,.24),mats[hair])


def lady_gossip():
    clear();m=common_materials();dress=material("Burgundy gossip dress",(.39,.055,.09,1),roughness=.9);shawl=material("Gold gossip shawl",(.62,.34,.08,1),roughness=.82)
    block("Long skirt",(0,.85,0),(.92,1.7,.72),dress,bevel=.1);block("Bodice",(0,1.75,0),(.72,1.0,.58),dress,bevel=.1);block("Shawl",(0,2.03,.12),(1.02,.26,.7),shawl,bevel=.08)
    for x,a in ((-.55,-.62),(.55,.62)):block("Animated gesturing arm",(x,1.88,.08),(.22,1.0,.24),dress,(0,0,a),.08)
    for x in (-.23,.23):block("Shoe and leg",(x,.28,.02),(.25,.56,.34),m["boot"],bevel=.07)
    face(m,bun=True);block("Gossip ribbon",(0,2.28,.32),(.3,.12,.08),shawl,bevel=.03)
    return export_glb("lady_gossip_3994.glb")


def lady_whispers():
    clear();m=common_materials();dress=material("Hushed teal dress",(.035,.24,.235,1),roughness=.92);veil=material("Whisper veil",(.025,.095,.11,1),roughness=.96)
    block("Quiet long skirt",(0,.85,0),(.9,1.7,.7),dress,bevel=.1);block("Quiet bodice",(0,1.72,0),(.68,1.0,.54),dress,bevel=.1)
    block("Lowered arm",(-.45,1.58,.06),(.2,1.0,.22),dress,(0,0,-.18),.07);block("Hand-near-mouth arm",(.4,2.02,.19),(.2,.88,.22),dress,(0,0,-.85),.07)
    for x in (-.22,.22):block("Soft shoe",(x,.25,.02),(.24,.5,.32),m["boot"],bevel=.07)
    face(m,skin="dark_skin",bun=False);block("Hushed veil",(0,2.72,-.2),(.82,.9,.32),veil,bevel=.12)
    return export_glb("lady_whispers_3995.glb")


def lady_speech():
    clear();m=common_materials();dress=material("Formal blue gown",(.055,.16,.43,1),roughness=.86);silver=material("Council silver",(.53,.58,.63,1),metallic=.45,roughness=.38);paper=material("Speech lesson",(.72,.63,.39,1),roughness=.95)
    block("Formal skirt",(0,.85,0),(.88,1.7,.68),dress,bevel=.08);block("Upright bodice",(0,1.78,0),(.66,1.08,.52),dress,bevel=.08)
    for x in (-.47,.47):block("Poised arm",(x,1.76,.03),(.2,1.05,.22),dress,(0,0,.08 if x<0 else -.08),.06)
    block("Held language tablet",(0,1.66,.43),(.72,.65,.08),paper,bevel=.04);block("Council collar",(0,2.22,.11),(.7,.16,.58),silver,bevel=.05)
    for x in (-.22,.22):block("Formal shoe",(x,.25,.02),(.24,.5,.32),m["boot"],bevel=.06)
    face(m,bun=True)
    return export_glb("lady_speech_3996.glb")


def old_man():
    clear();m=common_materials();coat=material("Ragged brown coat",(.17,.085,.035,1),roughness=1);shirt=material("Dirty old shirt",(.31,.27,.18,1),roughness=1);gold=material("Imperial office badge",(.72,.46,.075,1),metallic=.72,roughness=.38);wood=material("Walking stick",(.20,.085,.025,1),roughness=.9)
    for x in (-.24,.24):block("Bent boot and leg",(x,.55,.2),(.3,1.1,.38),m["boot"],(.35,0,0),.08)
    block("Slumped coat",(0,1.55,0),(.88,1.35,.68),coat,(.12,0,0),.12);block("Torn shirt",(0,1.8,.38),(.5,.62,.08),shirt,(.12,0,0),.04)
    block("Drooping arm",(-.53,1.5,.05),(.22,1.08,.24),coat,(0,0,-.12),.07);block("Pointing arm",(.62,1.82,.2),(.22,1.2,.24),coat,(0,0,-.72),.07)
    face(m,hair="gray");block("Scraggly beard",(0,2.43,.28),(.45,.5,.2),m["gray"],bevel=.1);block("Imperial badge",(.21,1.96,.44),(.22,.27,.06),gold,bevel=.03);block("Walking stick",(-.77,1.05,.18),(.1,2.1,.1),wood,(0,0,-.08),.03)
    return export_glb("old_man_3993.glb")


def lazy_guard():
    clear();m=common_materials();uniform=material("Dirty faded guard uniform",(.19,.25,.13,1),roughness=.95);armor=material("Tarnished guard metal",(.19,.21,.20,1),metallic=.62,roughness=.5);wood=material("Halberd shaft",(.24,.11,.035,1),roughness=.88)
    for x in (-.22,.22):block("Guard boot and leg",(x,.62,.03),(.28,1.24,.36),m["boot"],(0,0,-.05),.08)
    block("Leaning uniform coat",(0,1.62,0),(.82,1.4,.62),uniform,(0,0,.1),.1);block("Shoulder armor",(0,2.04,.02),(1.04,.25,.68),armor,(0,0,.1),.05)
    block("Guard arm",(-.52,1.62,.02),(.22,1.08,.24),uniform,(0,0,-.06),.06);block("Halberd grip arm",(.5,1.72,.15),(.22,1.05,.24),uniform,(0,0,-.22),.06)
    face(m);block("Guard helmet",(0,3.0,-.01),(.76,.28,.68),armor,bevel=.1);block("Nose guard",(0,2.78,.37),(.1,.4,.08),armor,bevel=.03)
    block("Halberd shaft",(.78,1.65,.05),(.1,3.3,.1),wood,(0,0,-.08),.03);block("Halberd axe blade",(.94,3.12,.05),(.55,.45,.12),armor,(0,0,-.08),.04)
    return export_glb("lazy_guard_3997.glb")


def wooden_dummy():
    clear();wood=material("Scarred practice wood",(.36,.19,.065,1),roughness=.96);cloth=material("Old draped clothing",(.24,.11,.075,1),roughness=1);dark=material("Painted target",(.45,.055,.03,1),roughness=.9);iron=material("Dummy fasteners",(.09,.1,.095,1),metallic=.62,roughness=.5)
    block("Wooden base",(0,.11,0),(1.5,.22,1.0),wood,bevel=.08);block("Left peg leg",(-.25,.72,0),(.25,1.35,.28),wood,bevel=.05);block("Right peg leg",(.25,.72,0),(.25,1.35,.28),wood,bevel=.05)
    block("Wooden torso",(0,1.72,0),(.72,1.35,.48),wood,bevel=.08);block("Crossbar arms",(0,1.94,0),(2.15,.24,.28),wood,bevel=.05);sphere("Carved wooden head",(0,2.78,0),(.4,.43,.38),wood)
    block("Draped old tunic",(0,1.65,.29),(.92,1.15,.12),cloth,bevel=.04);block("Target outer",(0,1.72,.37),(.48,.48,.05),dark,bevel=.16);block("Target center",(0,1.72,.405),(.19,.19,.05),iron,bevel=.08)
    for x in (-.8,.8):block("Iron arm fastener",(x,1.94,.17),(.14,.14,.05),iron,bevel=.04)
    return export_glb("wooden_dummy_3998.glb")


def render_preview(paths):
    clear(); offsets=(-7.5,-4.5,-1.5,1.5,4.5,7.5)
    for path,x in zip(paths,offsets):
        bpy.ops.import_scene.gltf(filepath=str(path)); imported=list(bpy.context.selected_objects)
        for obj in imported:obj.location += Vector((x,0,0))
    cube("Preview floor",(0,0,-.15),(19,4,.2),material("Preview floor mat",(.08,.085,.09,1),roughness=.95),.04)
    bpy.ops.object.camera_add(location=(11,-22,9));camera=bpy.context.object;camera.data.lens=52;camera.rotation_euler=(Vector((0,0,1.4))-camera.location).to_track_quat("-Z","Y").to_euler();bpy.context.scene.camera=camera
    bpy.ops.object.light_add(type="AREA",location=(-4,-7,10));bpy.context.object.data.energy=1900;bpy.context.object.data.size=9
    bpy.ops.object.light_add(type="AREA",location=(8,2,6));bpy.context.object.data.energy=900;bpy.context.object.data.color=(1,.55,.3);bpy.context.object.data.size=7
    scene=bpy.context.scene;scene.render.engine="BLENDER_EEVEE";scene.render.resolution_x=1400;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG";PREVIEW.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(PREVIEW);scene.world.color=(.012,.014,.018);bpy.ops.render.render(write_still=True)


def main():
    paths=[old_man(),lady_gossip(),lady_whispers(),lady_speech(),lazy_guard(),wooden_dummy()]
    render_preview(paths);print("Generated tutorial characters:",*(str(p) for p in paths),str(PREVIEW),sep="\n")


if __name__=="__main__":main()
