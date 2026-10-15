#!/usr/bin/env python3
"""Concept images of the RESTORED Burney Relief (as it left the workshop, not weathered), for Hyper3D Rodin.

    python3 models-src/rodin/make_burney_restored.py  ->  models-src/concepts/burney_restored_<strength>_<n>.png

img2img (InvokeAI, remote server) over a render of the scan (models-src/concepts/burney_scan_front.png; the scan is "The Burney Relief"
by danielpett, CC BY 4.0): the pose and the composition stay, the damage and the age go.
"""
import asyncio
import os
import pathlib
import sys

os.environ["INVOKEAI_BASE_URL"] = "http://10.11.18.22:9090"
sys.path.insert(0, os.path.expanduser("~/Projects/Packaging/mcp-server-invokeai"))
import httpx  # noqa: E402
import invokeai_mcp_server as inv  # noqa: E402

MODEL = "76cba3e7-6ed4-4fd6-b5c1-f72fcdd2297e"
OUT = pathlib.Path(__file__).resolve().parent.parent / "concepts"
PROMPT = ("a newly made Old Babylonian terracotta high relief plaque of the winged goddess Ishtar standing on two small lions lying down at her feet, "
          "with a tall owl standing on each side of her, owls with round faces and folded feathered wings, her feet are bird talons, "
          "front view, the plaque is complete with a straight rectangular frame and straight clean edges, perfectly intact, no cracks, no chips, "
          "no missing pieces, the neck and head are whole, she holds in each raised hand a rod with a ring, smooth clean pale fired clay, "
          "crisp sharp carving, evenly lit, museum photograph, highly detailed")
NEG = ("lions instead of owls, cracks, broken, chipped, damaged, weathered, eroded, dirty, stains, missing parts, ruin, worn, aged, gap in the neck, cartoon, anime, "
       "text, watermark, blurry, extra limbs, multiple figures, busy background, colour paint")


async def main():
    name = await inv._resolve_image(str(OUT / "burney_scan_front.png"))
    for strength in (0.25, 0.35):
        for n in (1, 2):
            graph = await inv.create_img2img_graph(name, PROMPT, NEG, strength=strength, model_key=MODEL, steps=35, cfg_scale=6.0,
                                                   scheduler="dpmpp_2m")
            _, out = await inv._run_graph(graph)
            async with httpx.AsyncClient(timeout=120) as c:
                r = await c.get(f"{inv.INVOKEAI_BASE_URL}/api/v1/images/i/{out}/full")
            (OUT / f"burney_restored_{strength}_{n}.png").write_bytes(r.content)
            print(strength, n, flush=True)


asyncio.run(main())
