"""Generate detailed original GLB environments for central Pendelhaven rooms 4165-4173."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_initial_room_models import ROOT, clear, cube, export_glb, material, sphere
from generate_training_route_models import rotated_cube, shell

PREVIEW=ROOT/"var"/"previews"/"pendelhaven-hub-models.png"

def cylinder(name,location,radius,depth,mat,vertices=16,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=location,rotation=rotation)
    obj=bpy.context.object;obj.name=name;obj.data.materials.append(mat);bpy.ops.object.shade_smooth();return obj

def torus(name,location,major,minor,mat,rotation=(math.pi/2,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=48,minor_segments=10,location=location,rotation=rotation)
    obj=bpy.context.object;obj.name=name;obj.data.materials.append(mat);return obj

def room_4165():
    clear();floor,wall,trim=shell(4165,{"N","E","S","W"},((.24,.28,.29,1),(.32,.27,.22,1),(.62,.51,.31,1)))
    stone=material("Weathered plaza stone",(.34,.38,.39,1),roughness=.92);wood=material("Oiled stage timber",(.24,.11,.04,1),roughness=.78);brass=material("Town brass",(.58,.37,.08,1),metallic=.65,roughness=.32);green=material("Planter foliage",(.09,.25,.11,1),roughness=.9)
    for x in (-6,-3,0,3,6):cube("Plaza paving",(x,-.015,0),(2.75,.06,16),stone,.025)
    cube("Crier stage",(0,.42,0),(5.2,.84,4.2),wood,.14);cube("Stage canopy",(0,3.5,0),(5.8,.18,4.8),material("Crier canvas",(.34,.075,.055,1),roughness=.9),.07)
    for x in (-2.55,2.55):cube("Canopy post",(x,1.95,0),(.16,3.9,.16),wood,.035)
    cube("Bulletin board",(3.8,1.45,2.25),(2.8,2.2,.16),wood,.08)
    for x,z in ((-5,-5),(5,-5),(-5,5),(5,5)):
        cylinder("Lamp post",(x,1.7,z),.1,3.4,brass,12);sphere("Warm lamp",(x,3.45,z),(.28,.38,.28),material("Lamp glass",(.9,.55,.18,1),roughness=.25))
        cylinder("Stone planter",(x*.72,.28,z*.72),.72,.55,stone,20);sphere("Plaza shrub",(x*.72,.9,z*.72),(.75,.8,.75),green)
    return export_glb("pendelhaven_square_4165.glb")

def room_4166():
    clear();floor,wall,trim=shell(4166,{"E","W","S"},((.17,.12,.08,1),(.29,.22,.16,1),(.56,.39,.21,1)))
    wood=material("Armor shop oak",(.23,.11,.04,1),roughness=.8);leather=material("Worked leather",(.28,.14,.055,1),roughness=.82);fur=material("Animal pelts",(.38,.29,.19,1),roughness=1);metal=material("Polished armor",(.43,.47,.48,1),metallic=.72,roughness=.3);brass=material("Coin scale brass",(.65,.42,.1,1),metallic=.7,roughness=.28)
    cube("Long fitting counter",(0,.82,-4.65),(10.5,1.64,1.5),wood,.12);cube("Counter top",(0,1.7,-4.65),(11,.16,1.8),wood,.06)
    for x in (-4.4,-2.2,0,2.2,4.4):
        cube("Hanging pelt",(x,2.5,-7.65),(1.65,2.65,.12),fur,.18);cube("Leather cuirass",(x,2.05,5.9),(1.3,1.7,.42),leather,.16);sphere("Armor shoulder",(x-.7,2.45,5.9),(.3,.32,.35),metal);sphere("Armor shoulder",(x+.7,2.45,5.9),(.3,.32,.35),metal)
    cylinder("Scale stand",(3.4,2.05,-4.65),.06,.7,brass,12);cube("Scale beam",(3.4,2.38,-4.65),(1.25,.08,.08),brass,.02)
    return export_glb("armor_shop_4166.glb")

def room_4167():
    clear();floor,wall,trim=shell(4167,{"W","S"},((.15,.105,.075,1),(.27,.19,.14,1),(.49,.33,.19,1)))
    stone=material("Forge stone",(.25,.23,.21,1),roughness=.93);iron=material("Forged iron",(.18,.2,.21,1),metallic=.8,roughness=.34);steel=material("Weapon steel",(.52,.57,.58,1),metallic=.82,roughness=.22);wood=material("Weapon hafts",(.29,.13,.045,1),roughness=.82);fire=material("Forge coals",(.95,.18,.025,1),roughness=.35)
    cube("Stone hearth",(-5.3,1.45,-5.7),(4.1,2.9,2.4),stone,.14);cube("Forge mouth",(-5.3,1.25,-4.45),(2.4,1.45,.2),fire,.18)
    cube("Blacksmith anvil",(-2.2,.78,-2.8),(1.6,.4,.65),iron,.1);cube("Anvil base",(-2.2,.38,-2.8),(.65,.8,.55),iron,.06)
    for x in (-3,0,3):
        cube("Weapon bin",(x,.65,1.9),(2.3,1.3,2.0),wood,.1)
        for i in range(5):rotated_cube("Displayed blade",(x-0.8+i*.4,1.75,1.9),(.09,.08,1.65),steel,(i-2)*.13,.02)
    for x in (-4.5,-2.25,0,2.25,4.5):cylinder("Bundled staff",(x,.95,5.7),.1,1.9,wood,12,rotation=(.12,0,0))
    return export_glb("weapon_shop_4167.glb")

def room_4168():
    clear();floor,wall,trim=shell(4168,{"N","S","W"},((.14,.095,.09,1),(.25,.18,.16,1),(.52,.32,.2,1)))
    chalk=material("Red summoning chalk",(.72,.035,.025,1),roughness=.8);stone=material("Arena dais stone",(.34,.3,.28,1),roughness=.86);wood=material("Gong frame",(.25,.11,.035,1),roughness=.82);brass=material("Arena gong brass",(.65,.38,.07,1),metallic=.72,roughness=.28);cloth=material("Arena banner",(.39,.035,.03,1),roughness=.9)
    torus("Outer summoning circle",(0,.03,0),3.15,.065,chalk);torus("Inner summoning circle",(0,.035,0),1.75,.045,chalk)
    for angle in range(0,360,45):
        x,z=math.sin(math.radians(angle))*2.45,math.cos(math.radians(angle))*2.45;rotated_cube("Summoning rune",(x,.045,z),(.5,.035,.16),chalk,math.radians(angle),.01)
    cube("Arena master dais",(5.1,.45,-2.8),(3.2,.9,2.5),stone,.12)
    for x in (4.05,6.15):cube("Gong frame",(x,2.15,-2.8),(.15,3.4,.15),wood,.035)
    cube("Gong crossbeam",(5.1,3.7,-2.8),(2.4,.16,.16),wood,.035);torus("Heavy arena gong",(5.1,2.45,-2.78),.78,.16,brass,rotation=(math.pi/2,0,0));sphere("Gong boss",(5.1,2.45,-2.58),(.2,.2,.12),brass)
    for x in (-5.8,0,5.8):cube("Arena banner",(x,3.05,-7.65),(1.35,2.6,.1),cloth,.05)
    return export_glb("pendelhaven_arena_4168.glb")

def room_4169():
    clear();floor,wall,trim=shell(4169,{"N","W"},((.22,.21,.24,1),(.36,.34,.39,1),(.63,.54,.71,1)))
    marble=material("Life altar marble",(.68,.66,.72,1),roughness=.58);purple=material("Myias purple cloth",(.28,.09,.38,1),roughness=.86);white=material("Hospice linens",(.73,.72,.67,1),roughness=.94);glass=material("Healing vial glass",(.42,.72,.78,1),roughness=.2);gold=material("Life sphere gold",(.72,.5,.12,1),metallic=.55,roughness=.32)
    cube("Sphere of Life altar",(0,.65,-.8),(4.4,1.3,3.5),marble,.18);sphere("Life sphere",(0,1.85,-.8),(.65,.65,.65),gold)
    for x,z in ((-5,-4),(5,-4),(-5,3.4),(5,3.4)):
        cube("Healing cot",(x,.45,z),(2.4,.9,3.4),white,.16);cube("Purple bed runner",(x,.92,z),(2.1,.08,1.0),purple,.04)
    for x in (-1.6,-.8,0,.8,1.6):cylinder("Healing vial",(x,1.42,.3),.09,.38,glass,12)
    return export_glb("pendelhaven_hospice_4169.glb")

def room_4170():
    clear();floor,wall,trim=shell(4170,{"N","E","W"},((.17,.12,.09,1),(.3,.23,.18,1),(.53,.37,.22,1)))
    wood=material("Guild timber",(.25,.12,.04,1),roughness=.84);leather=material("Protective sparring leather",(.35,.16,.055,1),roughness=.88);mat=material("Guild sparring mat",(.3,.055,.035,1),roughness=.97);iron=material("Balcony iron",(.16,.18,.18,1),metallic=.65,roughness=.42)
    cube("Central sparring mat",(0,.02,0),(8.5,.08,6.5),mat,.08)
    for x in (-4.8,4.8):
        cube("Training frame",(x,1.45,0),(2.0,2.9,.35),wood,.08);cube("Padded target",(x,1.6,.25),(1.25,1.5,.35),leather,.2)
    for z in (-6.7,6.7):cube("Upper balcony",(0,3.6,z),(12,.35,2.1),wood,.08)
    for x in range(-5,6):cube("Balcony rail",(x,4.25,-5.7),(.09,1.1,.09),iron,.02)
    return export_glb("pendelhaven_guild_4170.glb")

def room_4171():
    clear();floor,wall,trim=shell(4171,{"N","E"},((.16,.15,.13,1),(.27,.26,.23,1),(.58,.48,.27,1)))
    wood=material("Bank dark oak",(.18,.075,.025,1),roughness=.76);brass=material("Bank brass",(.67,.44,.11,1),metallic=.72,roughness=.28);iron=material("Teller bars",(.2,.22,.22,1),metallic=.7,roughness=.38);cloth=material("Coin bags",(.31,.19,.09,1),roughness=.95)
    for x in (-3.65,3.65):cube("Teller partition",(x,1.35,-4.75),(4.7,2.7,1.2),wood,.1);cube("Teller counter",(x,1.45,-3.95),(4.7,.25,1.2),wood,.06)
    cube("Public counter gate",(0,.18,-4.15),(2.5,.36,1.25),brass,.06)
    for x in (-4.5,-2.25,2.25,4.5):
        for dx in (-.55,0,.55):cube("Teller bar",(x+dx,2.75,-4.05),(.07,2.5,.08),iron,.02)
        cylinder("Coin stack",(x,1.72,-3.8),.22,.16,brass,20)
    for x,z in ((-5,1.5),(-3,3.2),(3,2),(5,4)):
        sphere("Appraisal sack",(x,.45,z),(.6,.7,.55),cloth);cylinder("Sealed coin",(x,.95,z),.14,.08,brass,20)
    return export_glb("pendelhaven_bank_4171.glb")

def room_4172():
    clear();floor,wall,trim=shell(4172,{"N","E","S"},((.2,.15,.09,1),(.31,.24,.15,1),(.56,.4,.2,1)))
    wood=material("General store shelves",(.24,.12,.04,1),roughness=.84);basket=material("Woven baskets",(.46,.3,.13,1),roughness=.93);fruit=material("Mixed fruit",(.58,.13,.06,1),roughness=.8);cloth=material("Travel packs",(.23,.28,.19,1),roughness=.94);dark=material("Down passage",(.015,.018,.02,1),roughness=1)
    for x in (-5,0,5):
        cube("Goods shelving",(x,2.0,-6.8),(3.5,4,.7),wood,.06)
        for y in (.65,1.6,2.55,3.5):cube("Shelf goods",(x,y,-6.3),(2.9,.4,.5),cloth,.08)
    for x,z in ((-4,-2),(-2,1),(2,-1),(4,2)):
        cylinder("Fruit basket",(x,.38,z),.72,.65,basket,20)
        for i in range(5):sphere("Basket fruit",(x+math.sin(i*2.1)*.35,.78,z+math.cos(i*2.1)*.35),(.2,.2,.2),fruit)
    cube("Central gear table",(0,.65,0),(3.4,1.3,3.4),wood,.14);cube("Trapdoor shadow",(-4.7,.03,4.8),(2.2,.08,2.2),dark,.04)
    return export_glb("general_store_4172.glb")

def room_4173():
    clear();floor,wall,trim=shell(4173,{"E","S"},((.13,.08,.045,1),(.23,.14,.085,1),(.48,.29,.13,1)))
    wood=material("Tavern oak",(.21,.085,.025,1),roughness=.8);ale=material("Amber ale",(.66,.28,.035,1),roughness=.28);metal=material("Tavern pewter",(.37,.4,.39,1),metallic=.58,roughness=.4);cloth=material("Tavern upholstery",(.31,.055,.035,1),roughness=.94);dark=material("Cellar stairs",(.012,.014,.016,1),roughness=1)
    cube("Long tavern bar",(0,.9,-5.2),(12.5,1.8,1.65),wood,.12);cube("Bar top",(0,1.84,-5.2),(13,.18,2.0),wood,.06)
    for x in (-5,-3,-1,1,3,5):cylinder("Ale mug",(x,2.08,-4.85),.18,.42,metal,16);cylinder("Amber ale",(x,2.28,-4.85),.145,.05,ale,16)
    for x,z in ((-4,-.5),(0,1),(4,-.5),(-2,4),(3,4)):
        cylinder("Patron table",(x,.76,z),1.15,.16,wood,24);cylinder("Table pedestal",(x,.38,z),.18,.76,wood,16)
        for angle in (0,math.pi):cylinder("Tavern stool",(x+math.sin(angle)*1.65,.42,z+math.cos(angle)*1.65),.42,.84,cloth,18)
    cube("Bones gaming cloth",(-2,1.0,4),(1.5,.04,1.5),cloth,.04);cube("Cellar stair shadow",(5.8,.03,5.5),(2.3,.08,2.5),dark,.04)
    return export_glb("pendelhaven_tavern_4173.glb")

def render_preview(paths):
    clear();offsets=[(-24,24),(0,24),(24,24),(-24,0),(0,0),(24,0),(-24,-24),(0,-24),(24,-24)]
    for path,(x,y) in zip(paths,offsets):
        bpy.ops.import_scene.gltf(filepath=str(path));imported=list(bpy.context.selected_objects)
        for obj in imported:obj.location+=Vector((x,y,0))
    bpy.ops.object.camera_add(location=(55,-68,62));camera=bpy.context.object;camera.data.lens=48;camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat("-Z","Y").to_euler();bpy.context.scene.camera=camera
    bpy.ops.object.light_add(type="AREA",location=(-10,-20,55));bpy.context.object.data.energy=4200;bpy.context.object.data.size=45
    scene=bpy.context.scene;scene.render.engine="BLENDER_EEVEE";scene.render.resolution_x=1500;scene.render.resolution_y=1050;scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG";PREVIEW.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(PREVIEW);scene.world.color=(.015,.017,.02);bpy.ops.render.render(write_still=True)

def main():
    paths=[room_4165(),room_4166(),room_4167(),room_4168(),room_4169(),room_4170(),room_4171(),room_4172(),room_4173()]
    render_preview(paths);print("Generated Pendelhaven hub rooms:",*(str(path) for path in paths),str(PREVIEW),sep="\n")

if __name__=="__main__":main()
