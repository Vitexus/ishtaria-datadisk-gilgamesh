"""Puts several glTF binaries (each with its own skeleton and `Idle` / `Walk` clips) into one model.

Used by tools/build_wagon.py: an ox cart is a cart, two oxen and a carter, which the engine draws as one character.

    parts = [Part("bull.glb", translation=(0.5, 0, 2.4), yaw_deg=0, scale=0.4), ...]
    write("wagon.glb", merge(parts, clips=("Idle", "Walk")))

Every part keeps its meshes, skin, materials and textures; its scene nodes become children of one wrapper node that
carries the part's translation, turn and scale. The clips of the same name are joined into one clip of the model: they
all run the whole length of the longest (the clip of a part that is shorter repeats a whole number of times in it), so the
oxen, the carter and whatever else moves stay in step as the model loops. Pure Python with numpy.
"""
import json
import math
import struct
from dataclasses import dataclass

import numpy as np

COMPONENT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


@dataclass
class Part:
    path: str
    translation: tuple = (0.0, 0.0, 0.0)
    yaw_deg: float = 0.0
    scale: float = 1.0
    name: str = "part"
    clips: bool = True        # False: the part stands still (a cart)


def read_glb(path):
    data = open(path, "rb").read()
    length = struct.unpack_from("<I", data, 12)[0]
    document = json.loads(data[20:20 + length])
    blob_at = 20 + length
    blob_length = struct.unpack_from("<I", data, blob_at)[0]
    blob = data[blob_at + 8:blob_at + 8 + blob_length]
    return document, bytearray(blob)


def accessor_array(document, blob, index):
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    width = WIDTH[accessor["type"]]
    dtype = np.dtype(COMPONENT[accessor["componentType"]])
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    stride = view.get("byteStride") or dtype.itemsize * width
    count = accessor["count"]
    if stride == dtype.itemsize * width:
        return np.frombuffer(blob, dtype=dtype, count=count * width, offset=start).reshape(count, width).copy()
    # elements spaced by a stride: take them one by one
    rows = [np.frombuffer(blob, dtype=dtype, count=width, offset=start + row * stride) for row in range(count)]
    return np.stack(rows).copy()


def yaw_quaternion(degrees):
    half = math.radians(degrees) / 2
    return [0.0, math.sin(half), 0.0, math.cos(half)]


def merge(parts, clips=("Idle", "Walk"), name="model"):
    out = {"asset": {"version": "2.0", "generator": "tools/compose_glb.py"}, "scene": 0, "scenes": [{"nodes": [0]}],
           "nodes": [{"name": name, "children": []}], "meshes": [], "skins": [], "materials": [], "textures": [],
           "images": [], "samplers": [], "accessors": [], "bufferViews": [], "buffers": [{"byteLength": 0}], "animations": []}
    blob = bytearray()
    channels = {clip: [] for clip in clips}              # clip -> [(target node, path, times, values, duration)]
    for number, part in enumerate(parts):
        document, source = read_glb(part.path)
        base = {key: len(out[key]) for key in ("nodes", "meshes", "skins", "materials", "textures", "images", "samplers", "accessors", "bufferViews")}
        offset = len(blob)
        blob += source + b"\0" * (-len(source) % 4)
        for view in document["bufferViews"]:
            moved = {**view, "byteOffset": view.get("byteOffset", 0) + offset}
            # The animation data of the parts is rewritten below; what is left of their interleaved views is no vertex data.
            if "target" not in moved:
                moved.pop("byteStride", None)
            out["bufferViews"].append(moved)
        for accessor in document["accessors"]:
            moved = dict(accessor)
            if "bufferView" in moved:
                moved["bufferView"] += base["bufferViews"]
            out["accessors"].append(moved)
        out["samplers"] += document.get("samplers", [])
        for image in document.get("images", []):
            out["images"].append({**image, "bufferView": image["bufferView"] + base["bufferViews"]})
        for texture in document.get("textures", []):
            moved = dict(texture)
            moved["source"] += base["images"]
            if "sampler" in moved:
                moved["sampler"] += base["samplers"]
            out["textures"].append(moved)
        for material in document.get("materials", []):
            text = json.dumps(material)
            moved = json.loads(text)
            for key in ("baseColorTexture", "metallicRoughnessTexture"):
                texture = moved.get("pbrMetallicRoughness", {}).get(key)
                if texture:
                    texture["index"] += base["textures"]
            for key in ("normalTexture", "occlusionTexture", "emissiveTexture"):
                if key in moved:
                    moved[key]["index"] += base["textures"]
            out["materials"].append(moved)
        for mesh in document.get("meshes", []):
            moved = json.loads(json.dumps(mesh))
            for primitive in moved["primitives"]:
                primitive["attributes"] = {key: value + base["accessors"] for key, value in primitive["attributes"].items()}
                if "indices" in primitive:
                    primitive["indices"] += base["accessors"]
                if "material" in primitive:
                    primitive["material"] += base["materials"]
            out["meshes"].append(moved)
        for skin in document.get("skins", []):
            moved = dict(skin)
            moved["joints"] = [joint + base["nodes"] + 1 for joint in skin["joints"]]
            if "inverseBindMatrices" in moved:
                moved["inverseBindMatrices"] += base["accessors"]
            if "skeleton" in moved:
                moved["skeleton"] += base["nodes"] + 1
            out["skins"].append(moved)
        # the part's wrapper is node base; its own nodes follow it
        wrapper = {"name": "%s_%d" % (part.name, number), "translation": list(part.translation),
                   "rotation": yaw_quaternion(part.yaw_deg), "scale": [part.scale] * 3, "children": []}
        out["nodes"].append(wrapper)
        for node in document["nodes"]:
            moved = dict(node)
            if "children" in moved:
                moved["children"] = [child + base["nodes"] + 1 for child in node["children"]]
            if "mesh" in moved:
                moved["mesh"] += base["meshes"]
            if "skin" in moved:
                moved["skin"] += base["skins"]
            out["nodes"].append(moved)
        wrapper["children"] = [node + base["nodes"] + 1 for node in document["scenes"][document.get("scene", 0)]["nodes"]]
        out["nodes"][0]["children"].append(base["nodes"])
        if part.clips:
            for animation in document.get("animations", []):
                if animation["name"] not in channels:
                    continue
                times_cache = {}
                for channel in animation["channels"]:
                    sampler = animation["samplers"][channel["sampler"]]
                    times = accessor_array(document, source, sampler["input"]).reshape(-1)
                    values = accessor_array(document, source, sampler["output"])
                    times_cache[sampler["input"]] = times
                    channels[animation["name"]].append((channel["target"]["node"] + base["nodes"] + 1, channel["target"]["path"], times, values))
    # the clips: one per name, the same length for every part
    for clip, items in channels.items():
        if not items:
            continue
        duration = max(float(times[-1]) for _, _, times, _ in items)
        samplers, joined = [], []
        for node, path, times, values in items:
            own = float(times[-1])
            repeats = max(1, round(duration / own)) if own > 0 else 1
            step = duration / repeats
            new_times, new_values = [], []
            for repeat in range(repeats):
                keep = slice(0, None) if repeat == 0 else slice(1, None)
                new_times.append((times * (step / own) + repeat * step)[keep] if own > 0 else times[keep])
                new_values.append(values[keep])
            times_array = np.concatenate(new_times).astype("<f4")
            values_array = np.concatenate(new_values).astype("<f4")
            accessors = []
            for array, kind, extra in ((times_array, "SCALAR", {"min": [float(times_array.min())], "max": [float(times_array.max())]}), (values_array, {1: "SCALAR", 2: "VEC2", 3: "VEC3", 4: "VEC4"}[values_array.shape[1]], {})):
                data = array.tobytes()
                out["bufferViews"].append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)})
                blob += data + b"\0" * (-len(data) % 4)
                out["accessors"].append({"bufferView": len(out["bufferViews"]) - 1, "componentType": 5126, "count": len(array), "type": kind, **extra})
                accessors.append(len(out["accessors"]) - 1)
            samplers.append({"input": accessors[0], "output": accessors[1], "interpolation": "LINEAR"})
            joined.append({"sampler": len(samplers) - 1, "target": {"node": node, "path": path}})
        out["animations"].append({"name": clip, "samplers": samplers, "channels": joined})
    for key in ("skins", "samplers", "images", "textures", "animations"):
        if not out[key]:
            del out[key]
    out["buffers"][0]["byteLength"] = len(blob)
    return out, blob


def write(path, built):
    document, blob = built
    text = json.dumps(document, separators=(",", ":")).encode()
    text += b" " * (-len(text) % 4)
    blob = bytes(blob) + b"\0" * (-len(blob) % 4)
    with open(path, "wb") as handle:
        handle.write(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(text) + 8 + len(blob)))
        handle.write(struct.pack("<I4s", len(text), b"JSON") + text + struct.pack("<I4s", len(blob), b"BIN\0") + blob)
