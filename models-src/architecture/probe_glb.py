import bpy
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
path = argv[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)

print("=== ACTIONS ===")
for a in bpy.data.actions:
    print("action:", a.name, "fcurves:", len(a.fcurves))

print("=== ARMATURES ===")
for obj in bpy.data.objects:
    if obj.type == "ARMATURE":
        print("armature:", obj.name)
        ad = obj.animation_data
        if ad:
            print("  anim action:", ad.action.name if ad.action else None)
            print("  nla tracks:", len(ad.nla_tracks))
            for t in ad.nla_tracks:
                for s in t.strips:
                    print("    strip:", s.name, "action:", s.action.name if s.action else None)
        for pb in obj.pose.bones:
            print("  bone:", pb.name, "parent:", pb.parent.name if pb.parent else None,
                  "head:", tuple(round(c, 3) for c in pb.head))

print("=== MESHES ===")
for obj in bpy.data.objects:
    if obj.type == "MESH":
        print("mesh:", obj.name, "verts:", len(obj.data.vertices),
              "parent:", obj.parent.name if obj.parent else None)
        for m in obj.data.materials:
            print("  mat:", m.name)
