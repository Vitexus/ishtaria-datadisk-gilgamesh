"""Paints the lamassu (aladlammu) in the colours of the museum reconstruction (research/lamassu-color.jpg).

    blender -b --python models-src/architecture/paint_lamassu.py -- models-src/lamassu/lamassu_derived_rodin_source.glb models-src/lamassu/lamassu_colored.glb

The Rodin source carries an AI stone texture; this script replaces its diffuse texture with a hand-painted one and
writes the coloured source that lamassu_models.py turns into lamassu_pair.glb and shedu_pair.glb. The regions are
chosen from the statue's geometry (the statue faces -Y, up is +Z, the head is at -Y): the horned crown on top of
the head, the human face, the dark beard hanging in front of the chest, the two wings raised over the rear half,
the brown bull body with the dark chest band, the banded legs, the black hooves and the dark tail. The palette is
the reconstruction's (the photo is underexposed, so these are its colours, not raw pixel samples): gold, lapis
lazuli, malachite green, carnelian red, ivory, warm brown, tan and near-black blue. A painted statue is matte
stone, so the metallic of the AI material is zeroed and the normal map is kept.

The paint is computed per vertex and rasterised into the existing UV map (the generated meshes are split along the
UV seams, so triangles are rasterised one by one, with their UV corners unwrapped across the 0/1 border); texels
no triangle covers (seam gaps) are filled from their painted neighbours.
"""
import sys

import bpy
import numpy as np

SRC, OUT = sys.argv[sys.argv.index("--") + 1:][:2]
TEX = 2048

# the reconstruction's palette (R, G, B in 0..255)
GOLD = (198, 156, 62)    # the horned crown
LAPIS = (36, 68, 138)    # lapis lazuli: the crown band, a wing stripe, the line under the chest band
GREEN = (74, 138, 88)    # malachite: a wing stripe
RED = (158, 54, 42)      # carnelian: a wing stripe, the belly band
CREAM = (226, 211, 172)  # ivory: the top wing stripe
BROWN = (128, 82, 52)    # the bull body
TAN = (168, 136, 104)    # the human face
BEARD = (28, 32, 48)     # the dark blue-black beard
BLACK = (24, 22, 20)     # the hooves, the dark bands, the tail

WING_BANDS = (RED, GREEN, LAPIS, CREAM)  # from the wing root up, so the top edge is ivory like in the photo


def vertex_normals(mesh, co):
    """Area-weighted vertex normals (Blender 4 has no calc_normals_split to read)."""
    acc = np.zeros_like(co)
    for p in mesh.polygons:
        idx = p.vertices
        if len(idx) < 3:
            continue
        n = np.cross(co[idx[1]] - co[idx[0]], co[idx[2]] - co[idx[0]])
        for i in idx:
            acc[i] += n
    length = np.linalg.norm(acc, axis=1)
    length[length == 0] = 1.0
    return acc / length[:, None]


def classify(co, no):
    """The reconstruction's colour of every vertex, from its position in the statue's own frame."""
    mn, mx = co.min(axis=0), co.max(axis=0)
    nx = (co[:, 0] - mn[0]) / (mx[0] - mn[0])
    ny = (co[:, 1] - mn[1]) / (mx[1] - mn[1])   # 0 = the face (-Y), 1 = the tail (+Y)
    nz = (co[:, 2] - mn[2]) / (mx[2] - mn[2])   # 0 = the ground, 1 = the top of the crown
    nnx = no[:, 0]
    nnz = no[:, 2]
    leg = (nz <= 0.42) & ((ny <= 0.34) | ((ny >= 0.45) & (ny <= 0.70))) & (np.abs(nx - 0.5) <= 0.35)

    col = np.empty((len(co), 3), np.float32)
    col[:] = np.array(BROWN, np.float32) / 255.0

    def put(mask, c):
        col[mask] = np.array(c, np.float32) / 255.0

    put((nz >= 0.895) & (ny <= 0.52), GOLD)                                           # the crown
    put((nz >= 0.875) & (nz < 0.895) & (ny <= 0.52), LAPIS)                           # the crown band
    put((nz >= 0.72) & (nz < 0.895) & (ny <= 0.40) & (np.abs(nx - 0.5) <= 0.35), TAN)  # the face
    put((nz >= 0.50) & (nz < 0.78) & (ny <= 0.14) & (np.abs(nx - 0.5) <= 0.28), BEARD)  # the beard curtain
    # the wings: the raised blades over the rear half; the back (up-facing, below 0.78) stays brown
    wing = (nz >= 0.64) & (ny >= 0.46) & (np.abs(nx - 0.5) <= 0.40) & ~((nnz > 0.6) & (nz <= 0.78))
    band = ((nz - 0.64) / 0.09).astype(int) % 4
    for i, c in enumerate(WING_BANDS):
        put(wing & (band == i), c)
    put((ny >= 0.88) & (nz <= 0.58), BLACK)                                           # the tail
    put(nz <= 0.075, BLACK)                                                           # the hooves
    put(leg & (nz >= 0.095) & (nz <= 0.135), BLACK)                                   # the ankle bands
    put(leg & (nz >= 0.29) & (nz <= 0.325), BLACK)                                    # the knee bands
    put((ny <= 0.52) & (nz >= 0.60) & (nz <= 0.665), BLACK)                           # the chest band
    put((ny <= 0.52) & (nz > 0.665) & (nz <= 0.685), LAPIS)                           # the line under it
    put((ny <= 0.45) & (nz >= 0.50) & (nz <= 0.525), RED)                             # the belly band
    return col


def rasterize(mesh, col, size):
    """Paints the per-vertex colours into a new texture through the mesh's UV map."""
    uv = mesh.uv_layers.active.data
    img = np.empty((size, size, 3), np.float32)
    img[:] = np.array(BROWN, np.float32) / 255.0
    covered = np.zeros((size, size), bool)
    tris = 0
    for p in mesh.polygons:
        idx = list(p.vertices)
        uvs = [tuple(uv[l].uv) for l in p.loop_indices]
        # a fan of triangles; each corner is shifted by whole turns to keep the triangle small (UV seams)
        for k in range(1, len(idx) - 1):
            corners = [uvs[0], uvs[k], uvs[k + 1]]
            vs = [idx[0], idx[k], idx[k + 1]]
            u = [c[0] for c in corners]
            v = [c[1] for c in corners]
            u[1] += round(u[0] - u[1])
            u[2] += round(u[0] - u[2])
            v[1] += round(v[0] - v[1])
            v[2] += round(v[0] - v[2])
            x0, x1 = min(u), max(u)
            y0, y1 = min(v), max(v)
            if (x1 - x0) * (y1 - y0) < 1e-12:
                continue
            # pixel bounds (image row 0 is the top, v = 1)
            px0 = max(0, int(np.floor(x0 * size)))
            px1 = min(size - 1, int(np.ceil(x1 * size)))
            py0 = max(0, int(np.floor((1.0 - y1) * size)))
            py1 = min(size - 1, int(np.ceil((1.0 - y0) * size)))
            if px1 < px0 or py1 < py0:
                continue
            gx = (np.arange(px0, px1 + 1) + 0.5) / size
            gy = 1.0 - (np.arange(py0, py1 + 1) + 0.5) / size
            uu = gx[None, :]
            vv = gy[:, None]
            d = (u[1] - u[0]) * (v[2] - v[0]) - (u[2] - u[0]) * (v[1] - v[0])
            if abs(d) < 1e-12:
                continue
            w1 = ((uu - u[0]) * (v[2] - v[0]) - (u[2] - u[0]) * (vv - v[0])) / d
            w2 = ((u[1] - u[0]) * (vv - v[0]) - (uu - u[0]) * (v[1] - v[0])) / d
            w0 = 1.0 - w1 - w2
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            c0, c1, c2 = (col[i] for i in vs)          # col is already 0..1
            rgb = w0[:, :, None] * c0 + w1[:, :, None] * c1 + w2[:, :, None] * c2
            img[py0:py1 + 1, px0:px1 + 1][inside] = rgb[inside]
            covered[py0:py1 + 1, px0:px1 + 1] |= inside
            tris += 1
    # fill the texels no triangle covered (seam gaps) from their painted neighbours
    for _ in range(4):
        if covered.all():
            break
        padded = np.pad(img, ((1, 1), (1, 1), (0, 0)), mode="edge")
        covp = np.pad(covered, ((1, 1), (1, 1)), mode="constant")
        acc = np.zeros_like(img)
        n = np.zeros(covered.shape, np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            shifted = np.roll(np.roll(covp, dy, axis=0), dx, axis=1)[1:-1, 1:-1]
            vals = np.roll(np.roll(padded, dy, axis=0), dx, axis=1)[1:-1, 1:-1]
            acc += vals * shifted[:, :, None]
            n += shifted
        fill = (~covered) & (n > 0)
        img[fill] = acc[fill] / n[fill, None]
        covered |= fill
    print(f"rasterised {tris} UV triangles, coverage {covered.mean() * 100:.2f}%")
    return img, covered


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=SRC)
    obj = max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.polygons))
    mesh = obj.data
    co = np.array([v.co[:] for v in mesh.vertices])
    col = classify(co, vertex_normals(mesh, co))
    names = {GOLD: "crown", LAPIS: "lapis", TAN: "face", BEARD: "beard", RED: "red", GREEN: "green",
             CREAM: "cream", BROWN: "body", BLACK: "black"}
    print("vertex colour counts:")
    for c, name in names.items():
        n = int((col == np.array(c, np.float32) / 255.0).all(axis=1).sum())
        print(f"  {name:8s} {n:6d}")
    img, covered = rasterize(mesh, col, TEX)

    # a new diffuse texture, a matte painted statue (no metallic), the AI normal map kept
    image = bpy.data.images.new("painted_diffuse", width=TEX, height=TEX)
    rgba = np.dstack([np.flipud(img), np.ones((TEX, TEX, 1), np.float32)])  # Blender image rows run bottom-up
    image.pixels = rgba.flatten()
    image.update()
    mat = mesh.materials[0]
    nt = mat.node_tree
    for n in nt.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.name.startswith("texture_diffuse"):
            n.image = image
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    for l in list(nt.links):
        if l.to_socket == bsdf.inputs["Metallic"]:
            nt.links.remove(l)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.85

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_yup=True,
                              export_image_format="AUTO", use_selection=True)
    print("wrote", OUT)


main()
