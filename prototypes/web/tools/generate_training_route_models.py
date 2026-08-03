"""Generate original low-poly room shells for tutorial rooms 3977-3982."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_initial_room_models import ROOT, clear, cube, export_glb, material


PREVIEW = ROOT / "var" / "previews" / "training-route-models.png"
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
ANGLES = {direction: index * math.pi / 4 for index, direction in enumerate(DIRECTIONS)}


def rotated_cube(name, location, scale, mat, angle=0.0, bevel=0.04):
    obj = cube(name, location, scale, mat, bevel)
    obj.rotation_euler.y = -angle
    return obj


def shell(room_id: int, exits: set[str], palette: tuple[tuple[float, float, float, float], ...]):
    floor = material(f"{room_id} floor", palette[0], roughness=0.94)
    wall = material(f"{room_id} wall", palette[1], roughness=0.9)
    trim = material(f"{room_id} trim", palette[2], roughness=0.75)
    dark = material(f"{room_id} passage", (0.018, 0.022, 0.026, 1), roughness=1)
    cube("Room floor", (0, -0.2, 0), (18, 0.4, 18), floor, 0.06)
    radius, width, opening = 8.35, 6.55, 2.5
    side_width = (width - opening) / 2
    for direction in DIRECTIONS:
        angle = ANGLES[direction]
        normal = (math.sin(angle), -math.cos(angle))
        tangent = (math.cos(angle), math.sin(angle))
        center = (normal[0] * radius, normal[1] * radius)
        if direction not in exits:
            rotated_cube(f"{direction} solid wall", (center[0], 2.4, center[1]), (width, 4.8, 0.42), wall, angle, 0.06)
            continue
        offset = opening / 2 + side_width / 2
        for sign, label in ((-1, "left"), (1, "right")):
            x = center[0] + tangent[0] * offset * sign
            z = center[1] + tangent[1] * offset * sign
            rotated_cube(f"{direction} doorway {label}", (x, 2.4, z), (side_width, 4.8, 0.42), wall, angle, 0.06)
        rotated_cube(f"{direction} doorway lintel", (center[0], 4.05, center[1]), (opening, 0.7, 0.56), trim, angle, 0.08)
        rotated_cube(f"{direction} passage shadow", (center[0] + normal[0] * .18, 1.65, center[1] + normal[1] * .18), (opening, 3.3, 0.12), dark, angle, 0)
    for direction in DIRECTIONS:
        angle = ANGLES[direction] + math.pi / 8
        x, z = math.sin(angle) * 8.72, -math.cos(angle) * 8.72
        rotated_cube("Corner column", (x, 2.25, z), (.42, 4.5, .42), trim, angle, .05)
    return floor, wall, trim


def room_3977() -> Path:
    clear(); floor, wall, trim = shell(3977, {"E", "W"}, ((.20,.12,.12,1),(.30,.22,.19,1),(.58,.39,.22,1)))
    cloth = material("Council red cloth", (.42,.08,.08,1), roughness=.88)
    paper = material("Lesson parchment", (.72,.58,.31,1), roughness=.95)
    cube("Recitation carpet", (0,-.01,0), (9,.08,4.2), cloth,.08)
    for x in (-3,0,3):
        cube("Speaker lectern", (x,.7,-2.7), (1.25,1.4,.85), trim,.08)
        cube("Lesson sheet", (x,1.44,-2.76), (.88,.05,.56), paper,.02)
    for z in (2.2,4.2): cube("Listener bench", (0,.35,z), (7,.7,.75), trim,.08)
    return export_glb("linguistic_council_3977.glb")


def room_3978() -> Path:
    clear(); floor, wall, trim = shell(3978, {"E", "NW"}, ((.16,.13,.09,1),(.22,.18,.12,1),(.39,.25,.11,1)))
    wood=material("Dark library wood",(.16,.075,.025,1),roughness=.87); book=material("Old book spines",(.36,.12,.07,1),roughness=.9); paper=material("Parchment pages",(.66,.52,.29,1),roughness=.96)
    for x in (-5.4,-2.7,0,2.7,5.4):
        cube("North bookcase",(x,2.0,-7.65),(2.25,4.0,.65),wood,.05)
        for row in range(4): cube("Books",(x, .55+row*.88,-7.25),(1.8,.42,.28),book,.02)
    cube("Reading table",(0,.65,1.0),(5.0,1.3,2.0),wood,.1)
    for x in (-1.45,0,1.45): cube("Open reference book",(x,1.34,1.0),(1.1,.06,.72),paper,.03)
    for x,z in ((-5,4),(4.8,4.8),(5,-3)): cube("Book stack",(x,.45,z),(1.2,.9,1.0),book,.05)
    return export_glb("help_library_3978.glb")


def room_3979() -> Path:
    clear(); floor, wall, trim = shell(3979, {"SE", "N"}, ((.18,.17,.14,1),(.25,.24,.20,1),(.38,.35,.25,1)))
    rubbish=material("Discarded cloth and paper",(.25,.18,.10,1),roughness=1); sign=material("Warning sign",(.53,.35,.13,1),roughness=.9); ink=material("Sign lettering",(.08,.04,.02,1),roughness=1)
    for i,(x,z) in enumerate(((-4,-3),(-2,3),(1,-4),(4,2),(5,-2),(-5,1))):
        rotated_cube("Discarded bundle",(x,.18+(.04*(i%2)),z),(1.2,.35,.8),rubbish,i*.43,.08)
    cube("West trash sign",(-7.7,2.2,0),(.12,2.1,3.4),sign,.06)
    for z in (-.85,-.28,.28,.85): cube("Sign mark",(-7.62,2.2,z),(.04,.12,2.1),ink,.01)
    return export_glb("discarded_hall_3979.glb")


def room_3980() -> Path:
    clear(); floor, wall, trim = shell(3980, {"S", "NE"}, ((.17,.15,.13,1),(.29,.25,.21,1),(.48,.36,.23,1)))
    wood=material("Wardroom racks",(.22,.11,.045,1),roughness=.86); leather=material("Boot leather",(.12,.06,.025,1),roughness=.78); steel=material("Knife steel",(.55,.58,.57,1),metallic=.72,roughness=.28)
    cube("East equipment rack",(7.55,1.7,1.0),(.65,3.4,8.0),wood,.06)
    for z in (-2.4,-.8,.8,2.4):
        cube("Boot pair",(7.1,.55,z),(.65,1.1,.85),leather,.08)
        rotated_cube("Display knife",(6.95,1.75,z),(.12,.08,.95),steel,.55,.02)
    cube("Changing bench",(-2,.42,2.8),(6,.84,1.1),wood,.08)
    return export_glb("wardroom_3980.glb")


def room_3981() -> Path:
    clear(); floor, wall, trim = shell(3981, {"SW", "E"}, ((.20,.14,.08,1),(.31,.22,.14,1),(.55,.39,.17,1)))
    wood=material("Market stall wood",(.24,.12,.04,1),roughness=.84); red=material("Red market cloth",(.46,.09,.055,1),roughness=.9); blue=material("Blue market cloth",(.06,.18,.34,1),roughness=.9); hide=material("Animal hide",(.34,.23,.13,1),roughness=1)
    for x,cloth in ((-4.2,red),(4.2,blue)):
        cube("Trader counter",(x,.72,-1.2),(3.2,1.45,1.4),wood,.08)
        cube("Hanging canopy",(x,3.2,-1.2),(3.8,.18,2.2),cloth,.06)
        for dx in (-1.55,1.55): cube("Canopy post",(x+dx,1.7,-1.2),(.14,3.4,.14),wood,.03)
    cube("Trading exchange table",(0,.55,3.2),(4.5,1.1,2.2),wood,.08)
    for x in (-1.2,0,1.2): rotated_cube("Folded hide",(x,1.16,3.2),(1,.12,1.25),hide,x*.2,.03)
    return export_glb("traders_pit_3981.glb")


def room_3982() -> Path:
    clear(); floor, wall, trim = shell(3982, {"W", "E"}, ((.16,.13,.11,1),(.27,.23,.20,1),(.46,.31,.19,1)))
    mat=material("Practice mat",(.25,.055,.035,1),roughness=.97); wood=material("Training weapon wood",(.29,.14,.05,1),roughness=.9); scripture=material("War scripture",(.66,.49,.24,1),roughness=.96)
    cube("Combat practice mat",(0,-.01,0),(9,.08,7),mat,.08)
    cube("North weapon rack",(0,1.45,-7.55),(6.5,2.9,.55),wood,.06)
    for x in (-2.4,-1.2,0,1.2,2.4): rotated_cube("Practice stave",(x,1.55,-7.15),(.16,2.5,.16),wood,x*.08,.03)
    cube("War scripture board",(5.9,2.15,-6.05),(2.1,2.7,.12),scripture,.06)
    return export_glb("practice_arena_3982.glb")


def render_preview(paths: list[Path]):
    clear()
    offsets=((-22,11),(0,11),(22,11),(-22,-11),(0,-11),(22,-11))
    for path,(x,y) in zip(paths,offsets):
        bpy.ops.import_scene.gltf(filepath=str(path)); imported=list(bpy.context.selected_objects)
        for obj in imported: obj.location += Vector((x,y,0))
    bpy.ops.object.camera_add(location=(39,-49,41)); camera=bpy.context.object; camera.data.lens=38
    camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat("-Z","Y").to_euler(); bpy.context.scene.camera=camera
    bpy.ops.object.light_add(type="AREA",location=(0,-5,35)); bpy.context.object.data.energy=3200; bpy.context.object.data.size=35
    scene=bpy.context.scene; scene.render.engine="BLENDER_EEVEE"; scene.render.resolution_x=1400; scene.render.resolution_y=800; scene.render.resolution_percentage=100; scene.render.image_settings.file_format="PNG"
    PREVIEW.parent.mkdir(parents=True,exist_ok=True); scene.render.filepath=str(PREVIEW); scene.world.color=(.015,.018,.022); bpy.ops.render.render(write_still=True)


def main():
    paths=[room_3977(),room_3978(),room_3979(),room_3980(),room_3981(),room_3982()]
    render_preview(paths)
    print("Generated route rooms:",*(str(path) for path in paths),str(PREVIEW),sep="\n")


if __name__=="__main__": main()
