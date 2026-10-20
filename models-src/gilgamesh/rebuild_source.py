"""Rebuild a game-friendly Rodin source from the raw Hyper3D PBR export.

    blender -b --python models-src/gilgamesh/rebuild_source.py

Keeps the original UVs and diffuse map (Rodin's paint). Welds UV-seam doubles so
Decimate no longer shatters the mesh into a triangle cloud, then reduces face count
and writes a compact JPEG-textured GLB for rodin_rig.py.
"""
import bmesh
import bpy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Full Hyper3D web export (PBR + Mixamo-style clips). Prefer this over a one-off Downloads extract.
SRC = os.path.join(HERE, "gilgamesh_rodin_raw.glb")
OUT = os.path.join(HERE, "gilgamesh_rodin_source.glb")
TARGET_FACES = 90000
TEX = 2048
WELD = 0.0008


def largest_mesh():
    return max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.polygons))


def island_sizes(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    seen = set()
    sizes = []
    for v0 in bm.verts:
        if v0.index in seen:
            continue
        stack = [v0]
        seen.add(v0.index)
        n = 0
        while stack:
            v = stack.pop()
            n += 1
            for e in v.link_edges:
                ov = e.other_vert(v)
                if ov.index not in seen:
                    seen.add(ov.index)
                    stack.append(ov)
        sizes.append(n)
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bm.free()
    sizes.sort(reverse=True)
    return sizes[:8], nm


def main():
    if not os.path.isfile(SRC):
        raise SystemExit("missing %s — copy the Hyper3D base_basic_pbr.glb export here first" % SRC)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=SRC)
    body = largest_mesh()
    for o in list(bpy.data.objects):
        if o is not body:
            bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.armatures):
        bpy.data.armatures.remove(a)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)

    body.name = "gilgamesh"
    body.parent = None
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bm = bmesh.new()
    bm.from_mesh(body.data)
    before = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD)
    bm.to_mesh(body.data)
    bm.free()
    body.data.update()
    print("welded", before, "->", len(body.data.vertices), "verts", len(body.data.polygons), "faces", flush=True)

    tops, nm = island_sizes(body)
    print("after weld islands", tops, "nonmanifold", nm, flush=True)

    if len(body.data.polygons) > TARGET_FACES:
        mod = body.modifiers.new("dec", "DECIMATE")
        mod.ratio = TARGET_FACES / len(body.data.polygons)
        bpy.ops.object.modifier_apply(modifier="dec")

    bm = bmesh.new()
    bm.from_mesh(body.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD)
    bm.to_mesh(body.data)
    bm.free()
    body.data.update()

    tops, nm = island_sizes(body)
    print(
        "final",
        len(body.data.vertices),
        "verts",
        len(body.data.polygons),
        "faces islands",
        tops,
        "nonmanifold",
        nm,
        flush=True,
    )

    # Keep only the diffuse map, resized for the package.
    mat = body.data.materials[0]
    diffuse = next(
        n.image
        for n in mat.node_tree.nodes
        if n.type == "TEX_IMAGE" and n.image and "diffuse" in n.image.name.lower()
    )
    if diffuse.size[0] != TEX or diffuse.size[1] != TEX:
        diffuse.scale(TEX, TEX)
    simple = bpy.data.materials.new("gilgamesh_body")
    simple.use_nodes = True
    nodes, links = simple.node_tree.nodes, simple.node_tree.links
    bsdf = nodes["Principled BSDF"]
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = diffuse
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
    body.data.materials.clear()
    body.data.materials.append(simple)

    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.export_scene.gltf(
        filepath=OUT,
        export_format="GLB",
        use_selection=True,
        export_animations=False,
        export_skins=False,
        export_image_format="JPEG",
    )
    print("wrote", OUT, os.path.getsize(OUT), flush=True)


if __name__ == "__main__":
    main()
    sys.exit(0)
