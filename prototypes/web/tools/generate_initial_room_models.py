"""Generate original low-poly GLB assets for Pendelhaven room 3976."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "prototypes" / "web" / "public" / "models" / "generated"
PREVIEW = ROOT / "var" / "previews" / "initial-room-models.png"


def clear() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def material(name: str, color: tuple[float, float, float, float], metallic=0.0, roughness=0.8, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = 3.0
    return mat


def cube(name, location, scale, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft stone edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def cylinder(name, location, radius, depth, mat, rotation=(0, 0, 0), vertices=10):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def sphere(name, location, scale, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def export_glb(name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    # Builders use Three.js coordinates (X right, Y up, Z depth). Convert them
    # to Blender's Z-up coordinates before the Blender -> glTF axis conversion.
    three_to_blender = Matrix.Rotation(math.pi / 2, 4, "X")
    for obj in bpy.context.scene.objects:
        obj.matrix_world = three_to_blender @ obj.matrix_world
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True, export_apply=True)
    return path


def build_room() -> Path:
    clear()
    stone = material("Warm worn stone", (0.22, 0.20, 0.16, 1), roughness=0.92)
    dark = material("Unlit blocked corridor", (0.025, 0.03, 0.035, 1), roughness=1)
    floor = material("Scuffed flagstones", (0.29, 0.255, 0.19, 1), roughness=0.98)
    trim = material("Aged sandstone trim", (0.38, 0.31, 0.20, 1), roughness=0.86)
    metal = material("Iron grating", (0.075, 0.08, 0.085, 1), metallic=0.7, roughness=0.45)
    ember = material("Torch ember", (0.8, 0.25, 0.035, 1), roughness=0.4, emission=(1.0, 0.16, 0.015, 1))

    cube("Flagstone floor", (0, -0.2, 0), (18, 0.4, 18), floor, 0.05)
    # Segmented walls leave four recognizable arch openings. West stays open.
    for z, side in ((-9, "North"), (9, "South")):
        cube(f"{side} wall left", (-5.6, 2.4, z), (6.8, 4.8, 0.45), stone, 0.08)
        cube(f"{side} wall right", (5.6, 2.4, z), (6.8, 4.8, 0.45), stone, 0.08)
    for x, side in ((-9, "West"), (9, "East")):
        cube(f"{side} wall near", (x, 2.4, -5.6), (0.45, 4.8, 6.8), stone, 0.08)
        cube(f"{side} wall far", (x, 2.4, 5.6), (0.45, 4.8, 6.8), stone, 0.08)
    for x, z, rotation, label in ((0, -9, (math.pi/2,0,0), "North"), (9, 0, (math.pi/2,0,math.pi/2), "East"), (0, 9, (math.pi/2,0,0), "South"), (-9, 0, (math.pi/2,0,math.pi/2), "West")):
        cube(f"{label} arch lintel", (x, 3.75, z), (3.8 if x == 0 else 0.5, 0.55, 0.5 if x == 0 else 3.8), trim, 0.12)
        if x == 0:
            cube(f"{label} arch left post", (-1.9, 1.75, z), (0.55, 3.5, 0.55), trim, 0.1)
            cube(f"{label} arch right post", (1.9, 1.75, z), (0.55, 3.5, 0.55), trim, 0.1)
        else:
            cube(f"{label} arch left post", (x, 1.75, -1.9), (0.55, 3.5, 0.55), trim, 0.1)
            cube(f"{label} arch right post", (x, 1.75, 1.9), (0.55, 3.5, 0.55), trim, 0.1)
    # N/E/S are visual corridors from the description but are sealed because the canonical graph has only W.
    cube("North blocked darkness", (0, 1.7, -9.25), (3.2, 3.4, 0.18), dark)
    cube("South blocked darkness", (0, 1.7, 9.25), (3.2, 3.4, 0.18), dark)
    cube("East blocked darkness", (9.25, 1.7, 0), (0.18, 3.4, 3.2), dark)
    for axis, base in (("N", (0, -9.48)), ("S", (0, 9.48))):
        for i in range(-2, 3):
            cube(f"{axis} grate {i}", (i * 0.48, 1.7, base[1]), (0.09, 3.2, 0.09), metal)
    for i in range(-2, 3):
        cube(f"E grate {i}", (9.48, 1.7, i * 0.48), (0.09, 3.2, 0.09), metal)
    # A westward flagstone guide reinforces the only authoritative passage.
    for i in range(5):
        cube(f"West guide stone {i}", (-1.4 - i * 1.35, -0.01, 0), (1.0, 0.08, 1.25), trim, 0.03)
    for x in (-5.7, 5.7):
        cube("Torch bracket", (x, 2.0, -8.72), (0.12, 0.5, 0.18), metal)
        cylinder("Torch flame", (x, 2.52, -8.55), 0.16, 0.48, ember, vertices=8)
    return export_glb("training_room_3976.glb")


def build_old_man() -> Path:
    clear()
    skin = material("Weathered skin", (0.44, 0.29, 0.19, 1), roughness=0.9)
    cloth = material("Ragged brown coat", (0.19, 0.115, 0.065, 1), roughness=1)
    cloth2 = material("Faded undershirt", (0.29, 0.25, 0.18, 1), roughness=1)
    gray = material("Unkempt gray hair", (0.28, 0.29, 0.27, 1), roughness=1)
    boot = material("Scuffed boots", (0.055, 0.04, 0.028, 1), roughness=0.95)
    gold = material("Worn imperial badge", (0.62, 0.42, 0.08, 1), metallic=0.72, roughness=0.42)
    wood = material("Walking stick", (0.21, 0.105, 0.04, 1), roughness=0.9)
    cylinder("Left boot and leg", (-0.25, 0.65, 0), 0.18, 1.3, boot, vertices=8)
    cylinder("Right boot and leg", (0.25, 0.65, 0.05), 0.18, 1.3, boot, vertices=8)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.62, radius2=0.45, depth=1.45, location=(0, 1.65, 0.05))
    bpy.context.object.name = "Slumped ragged coat"
    bpy.context.object.rotation_euler.x = math.radians(-9)
    bpy.context.object.data.materials.append(cloth)
    sphere("Head", (0, 2.62, 0.22), (0.38, 0.46, 0.38), skin)
    sphere("Messy hair", (0, 2.87, 0.17), (0.4, 0.23, 0.41), gray)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.3, radius2=0.08, depth=0.55, location=(0, 2.38, 0.47), rotation=(math.radians(78),0,0))
    bpy.context.object.name = "Drooping beard"
    bpy.context.object.data.materials.append(gray)
    for x, angle in ((-0.58, -18), (0.58, 24)):
        arm = cylinder("Hanging arm", (x, 1.66, 0.12), 0.13, 1.18, cloth2, rotation=(0, math.radians(angle), 0), vertices=8)
        arm.rotation_euler.x = math.radians(8)
    cube("Peeking office badge", (0.23, 1.93, -0.43), (0.25, 0.3, 0.055), gold, 0.03)
    cylinder("Walking stick", (0.78, 1.05, 0.25), 0.055, 2.1, wood, rotation=(0, math.radians(-8), 0), vertices=8)
    return export_glb("old_man_3993.glb")


def build_parchment() -> Path:
    clear()
    paper = material("Old parchment", (0.68, 0.49, 0.24, 1), roughness=0.96)
    edge = material("Dark parchment edge", (0.31, 0.17, 0.06, 1), roughness=1)
    ink = material("Faded abstract ink", (0.12, 0.07, 0.035, 1), roughness=1)
    tack = material("Iron tack", (0.08, 0.085, 0.09, 1), metallic=0.7, roughness=0.4)
    cube("Parchment sheet", (0, 0, 0), (1.35, 1.75, 0.055), paper, 0.06)
    cylinder("Top curled edge", (0, 0.86, 0.02), 0.085, 1.38, edge, rotation=(0, math.pi/2, 0), vertices=10)
    cylinder("Bottom curled edge", (0, -0.86, 0.02), 0.085, 1.38, edge, rotation=(0, math.pi/2, 0), vertices=10)
    for index, width in enumerate((0.88, 1.02, 0.72, 0.93, 0.6, 0.84)):
        cube(f"Abstract ink line {index}", (-0.1, 0.53 - index * 0.2, -0.045), (width, 0.035, 0.018), ink)
    sphere("Wall tack", (0, 0.69, -0.08), (0.09, 0.09, 0.05), tack)
    return export_glb("old_parchment_3985.glb")


def look_at(obj, target=(0, 2.5, 1.2)):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_preview(paths: list[Path]) -> None:
    clear()
    for path in paths:
        bpy.ops.import_scene.gltf(filepath=str(path))
        imported = list(bpy.context.selected_objects)
        if "old_man" in path.name:
            for obj in imported: obj.location += Vector((2.7, 6.5, 0))
        elif "parchment" in path.name:
            for obj in imported:
                obj.location += Vector((-2.6, 8.5, 2.0))
                obj.rotation_euler.z += math.pi
    bpy.ops.object.camera_add(location=(14.5, -16.5, 11.5))
    camera = bpy.context.object
    camera.data.lens = 28
    look_at(camera)
    bpy.context.scene.camera = camera
    bpy.ops.object.light_add(type="AREA", location=(0, -1, 8))
    bpy.context.object.data.energy = 1300
    bpy.context.object.data.shape = "DISK"
    bpy.context.object.data.size = 8
    bpy.ops.object.light_add(type="AREA", location=(-5, -4, 3))
    bpy.context.object.data.energy = 700
    bpy.context.object.data.color = (1.0, 0.55, 0.25)
    look_at(bpy.context.object)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(PREVIEW)
    scene.world.color = (0.012, 0.016, 0.025)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    paths = [build_room(), build_old_man(), build_parchment()]
    render_preview(paths)
    print("Generated:", *(str(path) for path in paths), str(PREVIEW), sep="\n")


if __name__ == "__main__":
    main()
