"""Shared helpers of the Gilgamesh character builder (Blender 4.x, Python API).

Everything is authored in metres, Z up, the character faces -Y (the glTF exporter turns that into +Z / +Y up,
which is what Ishtaria expects). Parts are small primitives that are weighted rigidly to one bone (or to
several for skirts), joined into one skinned mesh and exported as a glTF binary.
"""
import math
import os
import random

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in globals() else \
    "/home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh/models-src"
TEXDIR = os.path.join(HERE, "textures")

_mat_cache = {}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mat_cache.clear()
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.unit_settings.system = "METRIC"


def _tinted_image(tex, color):
    """The texture multiplied by the colour as a packed image, so that the glTF needs no colour node."""
    key = "img_%s_%.2f_%.2f_%.2f" % (tex, color[0], color[1], color[2])
    if key in bpy.data.images:
        return bpy.data.images[key]
    src = bpy.data.images.load(os.path.join(TEXDIR, tex + ".jpg"), check_existing=True)
    width, height = src.size
    pixels = list(src.pixels)
    count = len(pixels) // 4
    means = [max(sum(pixels[c::4]) / count, 0.05) for c in range(3)]
    out = bpy.data.images.new(key, width, height)
    result = pixels[:]
    for i in range(0, len(pixels), 4):
        for c in range(3):
            # keep 60 % of the texture contrast, scaled so that its average is the wanted colour
            p = means[c] + (pixels[i + c] - means[c]) * 0.4
            result[i + c] = max(0.0, min(1.0, p / means[c] * color[c]))
        result[i + 3] = 1.0
    out.pixels = result
    out.pack()
    out.file_format = "JPEG"
    return out


def material(name, color, tex=None, rough=0.85, metal=0.0, emit=None):
    key = (name, tuple(round(c, 3) for c in color), tex)
    if key in _mat_cache:
        return _mat_cache[key]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if tex:
        image = _tinted_image(tex, color)
        node = nodes.new("ShaderNodeTexImage")
        node.image = image
        mat.node_tree.links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (color[0] ** 2.2, color[1] ** 2.2, color[2] ** 2.2, 1.0)
    if emit is not None:
        bsdf.inputs["Emission Color"].default_value = (emit[0] ** 2.2, emit[1] ** 2.2, emit[2] ** 2.2, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.8
    _mat_cache[key] = mat
    return mat


def _finish(name, bm, mat, smooth=True):
    uv = bm.loops.layers.uv.verify()
    for face in bm.faces:
        for loop in face.loops:
            c = loop.vert.co
            loop[uv].uv = (c.x * 2.2 + c.y * 1.3, c.z * 2.5)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = smooth
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def sphere(name, center, radii, mat, segs=12, rings=8, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    cx, cy, cz = center
    rx, ry, rz = radii
    for v in bm.verts:
        v.co = Vector((v.co.x * rx + cx, v.co.y * ry + cy, v.co.z * rz + cz))
    return _finish(name, bm, mat, smooth)


def box(name, center, size, mat, smooth=False, rot_z=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    cx, cy, cz = center
    sx, sy, sz = size
    c, s = math.cos(rot_z), math.sin(rot_z)
    for v in bm.verts:
        x, y = v.co.x * sx, v.co.y * sy
        v.co = Vector((x * c - y * s + cx, x * s + y * c + cy, v.co.z * sz + cz))
    return _finish(name, bm, mat, smooth)


def cyl(name, p0, p1, r0, r1, mat, segs=10, caps=True, smooth=True):
    """A truncated cone from p0 (radius r0) to p1 (radius r1)."""
    p0, p1 = Vector(p0), Vector(p1)
    direction = p1 - p0
    length = max(direction.length, 1e-4)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segs,
                          radius1=max(r0, 1e-4), radius2=max(r1, 1e-4), depth=length)
    rotation = Vector((0, 0, 1)).rotation_difference(direction.normalized())
    middle = (p0 + p1) / 2
    for v in bm.verts:
        v.co = rotation @ v.co + middle
    return _finish(name, bm, mat, smooth)


def tube(name, rings, mat, segs=20, arc=None, tuft=0.0, smooth=True):
    """A lathe-like surface through rings (z, rx, ry, cx, cy). `arc` limits it to an angle range in degrees
    (0 = +X, 90 = back (+Y), 270 = front); `tuft` drops every other vertex of the last ring (fleece tufts)."""
    bm = bmesh.new()
    a0, a1 = (0.0, 360.0) if arc is None else arc
    closed = arc is None
    count = segs if closed else segs + 1
    grid = []
    for ri, (z, rx, ry, cx, cy) in enumerate(rings):
        row = []
        for k in range(count):
            a = math.radians(a0 + (a1 - a0) * k / segs)
            drop = tuft * (k % 2) if (tuft and ri == len(rings) - 1) else 0.0
            row.append(bm.verts.new((cx + rx * math.cos(a), cy + ry * math.sin(a), z - drop)))
        grid.append(row)
    for ri in range(len(rings) - 1):
        for k in range(segs if closed else segs):
            k2 = (k + 1) % count
            bm.faces.new((grid[ri][k], grid[ri][k2], grid[ri + 1][k2], grid[ri + 1][k]))
    return _finish(name, bm, mat, smooth)


def cone_tufts(prefix, mat, base_points, length, radius, direction=(0, 0, -1), jitter=0.35, seed=1):
    """Many small cones, one per base point (fur tufts, spikes). Returns one joined object."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    for p in base_points:
        d = Vector(direction) + Vector((rnd.uniform(-jitter, jitter), rnd.uniform(-jitter, jitter), rnd.uniform(-jitter, jitter)))
        d.normalize()
        tip = Vector(p) + d * length * rnd.uniform(0.7, 1.2)
        res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=5, radius1=radius, radius2=0.0001, depth=1.0)
        rotation = Vector((0, 0, 1)).rotation_difference((tip - Vector(p)).normalized())
        ln = (tip - Vector(p)).length
        for v in res["verts"]:
            v.co = rotation @ Vector((v.co.x, v.co.y, (v.co.z + 0.5) * ln)) + Vector(p)
    return _finish(prefix, bm, mat)


def surface_points(p0, p1, radius, count, seed=3, front_bias=0.0):
    """Random points on a cylinder surface between p0 and p1 (for fur)."""
    rnd = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    axis = (p1 - p0)
    ax = axis.normalized()
    ref = Vector((1, 0, 0)) if abs(ax.x) < 0.9 else Vector((0, 1, 0))
    u = ax.cross(ref).normalized()
    w = ax.cross(u)
    out = []
    for _ in range(count):
        t = rnd.random()
        a = rnd.uniform(0, 2 * math.pi)
        out.append(p0 + axis * t + (u * math.cos(a) + w * math.sin(a)) * radius)
    return out


_skin = {}


def assign(obj, bone=None, weights=None, groups=()):
    """Remember the skinning of a part: one bone, or weights(vertex position) -> {bone: weight}."""
    _skin[obj.name] = (bone, weights, tuple(groups))
    return obj


def skin_of(obj):
    return _skin.get(obj.name, (None, None, ()))


_wfuncs = {}


def set_weights(obj, func):
    _wfuncs[obj.name] = func


def get_weights(obj):
    return _wfuncs.get(obj.name)


def smoothstep(a, b, x):
    if b == a:
        return 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)
