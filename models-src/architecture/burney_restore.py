"""Restores the Burney Relief scan and cuts the figures free of the slab (runs in Blender, live window or headless).

    blender -b --python models-src/architecture/burney_restore.py -- models-src/burney_relief/scene.gltf media/models/architecture/burney_relief.glb
    (live window: exec(open(<this file>).read()) after setting RESTORE_ARGS = [scene.gltf, out.glb | None])

Source: "The Burney Relief" by danielpett (https://sketchfab.com/3d-models/the-burney-relief-217a01bf2d324ad19a05e54256b2824e), CC BY 4.0.
The owner wants the goddess as she left the workshop (research notes: models-src/burney_relief/RESTORATION.md):

1. MIRROR: the relief was symmetric about the goddess's centre line (AXIS_X), the left half survives: the right ear, hair roll, cheek,
   neck and half of the necklace are broken off. The surviving left faces of that region are mirrored onto the right with their UVs, so the
   colour comes along; the broken original faces are removed, the patch lies a hair in front so that it covers the rim.
2. CUT: the slab is not flat (it leans and has a step along the crack), so the figures are found by their height over a fitted slab plane
   (PLANE) plus two outlines for the low-relief wings; only the large connected pieces are kept (the goddess, the owls, the lions).
3. CLOSE: the holes inside the figure are filled and a thin shell (Solidify) closes the back, which replaces the slab.
Units of the source scan: the plaque is about 34 x 45 units; the front looks along -Y; z is up.
"""
import sys

import bmesh
import bpy
import cv2
import numpy as np
from matplotlib.path import Path
from mathutils import Vector
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

AXIS_X = 0.68                       # centre line of the goddess (found by mirroring the height map, see RESTORATION.md)
PLANE = (-0.0148, 0.0982, -4.488)   # slab: y = a*x + b*z + c
FIGURE_MIN_HEIGHT = 0.45            # units in front of the slab plane
SHELL = 0.35                        # thickness of the back shell, units
WING_L = [(-2.83, 17.55), (-4.09, 16.76), (-4.72, 15.35), (-5.19, 13.46), (-5.66, 11.41), (-6.45, 8.74), (-7.39, 6.23), (-8.33, 4.02),
          (-8.8, 2.61), (-7.39, 2.55), (-5.5, 3.18), (-3.62, 4.02), (-2.2, 4.97), (-1.57, 8.43), (-1.57, 14.09), (-2.04, 16.6)]
WING_R = [(2 * 0.68 - x, z) for x, z in WING_L]   # the right half is the mirror image of the left one
# the rod and ring (measuring rod and coiled line) the goddess holds in each hand: on the slab they are only low relief and an engraved circle, so
# they are modelled new, in the scan's units (front view x, z; y is the depth of the palm). Measured from orthographic views of the scan:
# right hand palm centre (8.4, 16.5), ring centre (8.84, 18.63) r 1.6, rod (5.44, 17.81) -> (12.24, 16.9); the left hand is the mirror image about
# its own palm centre (-7.86, 17.1) (its rod fragments and the faint ring circle are where this puts them).
ROD_RADIUS = 0.17
RING_RADIUS, RING_TUBE = 1.5, 0.17
RODS = [  # (rod p0, rod p1, ring centre): the left hand's, measured; the right hand's is the mirror image
    ((-4.9, 18.41), (-11.7, 17.5), (-8.3, 19.23)),
]
RODS += [((2 * 0.68 - a[0], a[1]), (2 * 0.68 - b[0], b[1]), (2 * 0.68 - c[0], c[1])) for a, b, c in RODS]
ROD_Y, RING_Y = -3.35, -2.95
# the hands are low relief too (palm and fingers a few tenths of a unit over the slab, which leans there): outlines traced from the scan; inside them
# a vertex counts as hand when it stands HAND_MIN_HEIGHT in front of the median slab level found just outside the outline
HAND_L = [(-9.0, 18.39), (-8.7, 19.19), (-8.3, 19.39), (-7.8, 19.09), (-7.5, 18.49), (-7.1, 17.79), (-6.7, 17.49), (-6.64, 16.59),
          (-6.9, 15.79), (-7.2, 15.09), (-8.0, 15.19), (-8.5, 16.09), (-8.8, 17.09), (-9.1, 17.89)]
HAND_R = [(2 * 0.68 - x, z) for x, z in HAND_L]
HAND_MIN_HEIGHT = 0.05
# colours (owner's wish, 2026-10-13): pink skin, gold necklace and gold rod and ring; hair, hat, wings, owls and lions stay stone
SKIN_RGB = (0.93, 0.62, 0.58)
GOLD_RGB = (1.0, 0.766, 0.336)
TARGET_FACES = 60000
TEX = 2048
HEIGHT_M = 2.4


def mirrored_region(xr, z, grow=0.0, axis_grow=0.0):
    """The whole half of the figure on one side of the axis (the owner: the statue was symmetric, the left half survives better): x_rel >= 0."""
    return xr >= -axis_grow


def load(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")   # the glTF root empties carry the scene scale
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = "BurneyRelief"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in list(bpy.data.objects):
        if o.type == "EMPTY":
            bpy.data.objects.remove(o, do_unlink=True)
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)
    bm.to_mesh(obj.data); bm.free()
    return obj


def face_centres(me):
    nf = len(me.polygons)
    c = np.empty(nf * 3, np.float32); me.polygons.foreach_get("center", c)
    return c.reshape(-1, 3)


def mirror_patch(obj):
    me = obj.data
    # 1) cut the faces that straddle the axis exactly on it, so the two halves meet on one line
    bm = bmesh.new(); bm.from_mesh(me)
    hi_faces = list(bm.faces)
    geom = list(hi_faces) + list({e for f in hi_faces for e in f.edges}) + list({v for f in hi_faces for v in f.verts})
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(AXIS_X, 0, 0), plane_no=(1, 0, 0), dist=1e-5)
    bm.to_mesh(me); bm.free()
    cen = face_centres(me)
    xr_m = (2 * AXIS_X - cen[:, 0]) - AXIS_X
    src = np.where(mirrored_region(xr_m, cen[:, 2]) & (cen[:, 0] < AXIS_X))[0]
    kill = np.where(mirrored_region(cen[:, 0] - AXIS_X, cen[:, 2], grow=-0.06) & (cen[:, 0] > AXIS_X))[0]
    pm = me.copy()
    patch = bpy.data.objects.new("mirror_patch", pm)
    bpy.context.collection.objects.link(patch)
    bm = bmesh.new(); bm.from_mesh(pm); bm.faces.ensure_lookup_table()
    keep = set(int(i) for i in src)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
    for v in bm.verts:
        on_axis = abs(v.co.x - AXIS_X) < 1e-4
        v.co.x = 2 * AXIS_X - v.co.x
        if not on_axis:
            v.co.y -= 0.012        # a hair in front of the rim it overlaps (not on the axis, where the halves are welded)
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:])    # mirroring turned the faces inside out
    bm.to_mesh(pm); bm.free()
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    kl = set(int(i) for i in kill)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index in kl], context="FACES")
    bm.to_mesh(me); bm.free()
    print("mirror patch:", len(src), "faces added,", len(kill), "removed")
    bpy.ops.object.select_all(action="DESELECT")
    patch.select_set(True); obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    # the two halves share the vertices on the axis (same position, same UV): weld exactly those
    me = obj.data
    bm = bmesh.new(); bm.from_mesh(me)
    axis_verts = [v for v in bm.verts if abs(v.co.x - AXIS_X) < 1e-4]
    bmesh.ops.remove_doubles(bm, verts=axis_verts, dist=1e-4)
    bm.to_mesh(me); bm.free()


def figure_faces(obj):
    me = obj.data
    n = len(me.vertices); nf = len(me.polygons)
    co = np.empty(n * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3).astype(np.float64)
    prot = (PLANE[0] * co[:, 0] + PLANE[1] * co[:, 2] + PLANE[2]) - co[:, 1]
    include = prot > FIGURE_MIN_HEIGHT
    for poly in (WING_L, WING_R):
        include |= Path(poly).contains_points(co[:, [0, 2]])
    for poly in (HAND_L, HAND_R):
        inside = Path(poly).contains_points(co[:, [0, 2]])
        near = Path(poly).contains_points(co[:, [0, 2]], radius=-1.2)       # outline grown by 1.2 units (sign of radius depends on the winding)
        near |= Path(poly).contains_points(co[:, [0, 2]], radius=1.2)
        ring = near & ~inside & (prot < FIGURE_MIN_HEIGHT)                  # the slab around the hand, not the arm
        ref = np.median(co[ring, 1]) if ring.sum() > 20 else co[inside, 1].max()
        include |= inside & (co[:, 1] < ref - HAND_MIN_HEIGHT)
        print("hand: slab level", round(float(ref), 2), "ring verts", int(ring.sum()), "hand verts", int((inside & (co[:, 1] < ref - HAND_MIN_HEIGHT)).sum()))
    vi = np.empty(len(me.loops), np.int32); me.loops.foreach_get("vertex_index", vi)
    ei = np.empty(len(me.loops), np.int32); me.loops.foreach_get("edge_index", ei)
    tot = np.empty(nf, np.int32); me.polygons.foreach_get("loop_total", tot)
    fol = np.repeat(np.arange(nf), tot)
    fkeep = np.bincount(fol, weights=include[vi].astype(float), minlength=nf) / tot >= 0.99
    order = np.argsort(ei); es = ei[order]; fs = fol[order]
    same = es[1:] == es[:-1]
    a, b = fs[:-1][same], fs[1:][same]
    ok = fkeep[a] & fkeep[b]
    g = coo_matrix((np.ones(ok.sum()), (a[ok], b[ok])), shape=(nf, nf))
    ncomp, lab = connected_components(g, directed=False)
    cnt = np.bincount(lab[fkeep], minlength=ncomp)
    final = fkeep & (cnt[lab] > 1500)       # the goddess with the owls and the lions, and the mirrored patch
    print("figure pieces:", sorted((int(c) for c in cnt if c > 1500), reverse=True), "faces", int(final.sum()))
    return final


def cut_and_close(obj, final):
    me2 = obj.data.copy(); me2.name = "Goddess_mesh"
    g = bpy.data.objects.new("Goddess", me2)
    bpy.context.collection.objects.link(g)
    bm = bmesh.new(); bm.from_mesh(me2); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not final[f.index]], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    # holes inside the figure (between chin and necklace): only small loops are filled, the outline and long cracks are not (welding the
    # axis strip and filling larger loops made long spikes, tried 2026-10-13)
    bnd = [e for e in bm.edges if e.is_boundary]
    res = bmesh.ops.holes_fill(bm, edges=bnd, sides=60)
    print("holes filled with", len(res["faces"]), "faces")
    # the new faces have no UVs: borrow them (and the material) from the surrounding faces, so they take the colour of the stone around
    uv = bm.loops.layers.uv.active
    filled = set(res["faces"])
    for f in filled:
        for l in f.loops:
            near = [o for o in l.vert.link_loops if o.face not in filled]
            if near:
                l[uv].uv = near[0][uv].uv
                f.material_index = near[0].face.material_index
    bm.to_mesh(me2); bm.free()
    bpy.ops.object.select_all(action="DESELECT")
    g.select_set(True); bpy.context.view_layer.objects.active = g
    m = g.modifiers.new("shell", "SOLIDIFY")
    m.thickness = SHELL; m.offset = -1.0; m.use_even_offset = True; m.use_rim = True
    bpy.ops.object.modifier_apply(modifier="shell")
    return g


def material_index(g, kind):
    """Slot of a plain material in g: 'skin' (pink) or 'gold' (metal); created on first use."""
    name = {"skin": "skin_pink", "gold": "gold"}[kind]
    for i, m in enumerate(g.data.materials):
        if m and m.name == name:
            return i
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    if kind == "gold":
        b.inputs["Base Color"].default_value = (*GOLD_RGB, 1); b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.3
    else:
        b.inputs["Base Color"].default_value = (*SKIN_RGB, 1); b.inputs["Metallic"].default_value = 0.0; b.inputs["Roughness"].default_value = 0.55
    g.data.materials.append(mat)
    return len(g.data.materials) - 1


def apply_colours(g):
    """Pink skin and gold necklace as plain materials, chosen by region and height over the slab plane (front view, scan units)."""
    me = g.data
    nf = len(me.polygons)
    cen = face_centres(me)
    x, y, z = cen[:, 0], cen[:, 1], cen[:, 2]
    p = (PLANE[0] * x + PLANE[1] * z + PLANE[2]) - y
    xr = x - AXIS_X
    gold = (np.abs(xr) <= 2.3) & (z >= 15.6) & (z <= 17.3) & (p > 0.3)                                  # collar, pendants, tassels
    face = (z > 17.3) & (((xr / 1.7) ** 2 + ((z - 19.8) / 2.7) ** 2) < 1.0)                              # face and neck
    body = (np.abs(xr) < 2.8) & (z > -12.0) & (z <= 15.6) & (p > 0.15)    # torso and legs (talons below z = -12 stay stone)                                      # torso, legs
    hands = np.zeros(nf, bool)
    for poly in (HAND_L, HAND_R):
        hands |= Path(poly).contains_points(cen[:, [0, 2]])
    arms = (np.abs(xr) >= 2.0) & (np.abs(xr) < 10.6) & (z > 9.0) & (z < 19.8) & ((p > 0.5) | hands)  # arms and hands
    skin = (face | body | arms) & ~gold
    si, gi = material_index(g, "skin"), material_index(g, "gold")
    mi = np.empty(nf, np.int32); me.polygons.foreach_get("material_index", mi)
    mi[skin] = si; mi[gold] = gi
    me.polygons.foreach_set("material_index", mi)
    print("skin faces", int(skin.sum()), "gold faces", int(gold.sum()), "of", nf)


def add_rods(g):
    """Rod and ring in each hand as new geometry with the gold material (joined into g)."""
    import math
    mi = material_index(g, "gold")
    bm = bmesh.new(); bm.from_mesh(g.data)
    new_faces = []
    for p0, p1, rc in RODS:
        a = Vector((p0[0], ROD_Y, p0[1])); c = Vector((p1[0], ROD_Y, p1[1]))
        axis = c - a
        mid = (a + c) / 2
        rot = axis.to_track_quat("Z", "Y").to_matrix().to_4x4()
        cone = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=ROD_RADIUS, radius2=ROD_RADIUS, depth=axis.length)
        bmesh.ops.transform(bm, matrix=__import__("mathutils").Matrix.Translation(mid) @ rot, verts=cone["verts"])
        # ring: a torus in the x-z plane
        major, minor = 56, 14
        centre = Vector((rc[0], RING_Y, rc[1]))
        grid = []
        for i in range(major):
            t = 2 * math.pi * i / major
            row = []
            for j in range(minor):
                u = 2 * math.pi * j / minor
                rr = RING_RADIUS + RING_TUBE * math.cos(u)
                row.append(bm.verts.new(centre + Vector((rr * math.cos(t), RING_TUBE * math.sin(u), rr * math.sin(t)))))
            grid.append(row)
        for i in range(major):
            for j in range(minor):
                new_faces.append(bm.faces.new((grid[i][j], grid[(i + 1) % major][j], grid[(i + 1) % major][(j + 1) % minor], grid[i][(j + 1) % minor])))
        new_faces.extend(f for f in bm.faces if all(v in cone["verts"] for v in f.verts))
    for f in new_faces:
        f.material_index = mi
    bmesh.ops.recalc_face_normals(bm, faces=new_faces)
    bm.to_mesh(g.data); bm.free()


def export(g, out):
    """Decimate, scale to HEIGHT_M, feet on z=0, textures down, exported with the front along -Y."""
    mod = g.modifiers.new("dec", "DECIMATE")
    mod.ratio = min(1.0, TARGET_FACES / len(g.data.polygons))
    bpy.ops.object.select_all(action="DESELECT"); g.select_set(True); bpy.context.view_layer.objects.active = g
    bpy.ops.object.modifier_apply(modifier="dec")
    add_rods(g)
    co = np.array([v.co[:] for v in g.data.vertices])
    mn, mx = co.min(axis=0), co.max(axis=0)
    s = HEIGHT_M / (mx[2] - mn[2])
    cx = (mn[0] + mx[0]) / 2
    for v in g.data.vertices:
        v.co = Vector(((v.co.x - cx) * s, (v.co.y - mx[1]) * s, (v.co.z - mn[2]) * s))
    g.data.update()
    print("faces", len(g.data.polygons), "size m", (mx - mn) * s)
    for img in bpy.data.images:
        if img.size[0] > TEX:
            img.scale(TEX, int(TEX * img.size[1] / img.size[0]))
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_yup=True, export_image_format="JPEG", export_jpeg_quality=85,
                              use_selection=True)   # only the restored figures, not the hidden full scan
    print("exported", out)


def run(scene_gltf, out_glb=None):
    obj = load(scene_gltf)
    mirror_patch(obj)
    final = figure_faces(obj)
    g = cut_and_close(obj, final)
    apply_colours(g)
    obj.hide_set(True)
    if out_glb:
        export(g, out_glb)
    return g


if "RESTORE_ARGS" in globals():
    run(*RESTORE_ARGS)
elif "--" in sys.argv:
    run(*sys.argv[sys.argv.index("--") + 1:][:2])
