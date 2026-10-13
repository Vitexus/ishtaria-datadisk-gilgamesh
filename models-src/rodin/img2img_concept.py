#!/usr/bin/env python3
"""Variant of a concept image with the same pose (InvokeAI img2img, remote server).

    python3 models-src/rodin/img2img_concept.py <pose.png> <out_prefix> <strength> "<prompt>"
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
NEG = ("hands together, arms raised, nude, cropped, close-up, modern clothing, cartoon, anime, text, watermark, blurry, "
       "extra limbs, deformed hands, multiple people, busy background, tall headdress")


async def main():
    pose, prefix, strength, prompt = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    name = await inv._resolve_image(str(pathlib.Path(pose).resolve()))
    for n in (1, 2):
        graph = await inv.create_img2img_graph(name, prompt, NEG, strength=strength, model_key=MODEL, steps=35, cfg_scale=6.0,
                                               scheduler="dpmpp_2m")
        _, out = await inv._run_graph(graph)
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.get(f"{inv.INVOKEAI_BASE_URL}/api/v1/images/i/{out}/full")
        pathlib.Path(f"{prefix}_i2i_{n}.png").write_bytes(r.content)
        print(prefix, n, flush=True)


asyncio.run(main())
