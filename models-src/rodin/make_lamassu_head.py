#!/usr/bin/env python3
"""Concept images of the lamassu's human head for Hyper3D Rodin (SDXL cannot draw head and bull body together).

    python3 models-src/rodin/make_lamassu_head.py  ->  models-src/concepts/lamassu_head_<n>.png
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
PROMPT = ("front view of a monumental Assyrian limestone sculpture of the head and neck of a bearded man, calm human face, straight nose, almond eyes, "
          "thin lips, long square-cut curled beard hanging to the chest, tall cylindrical tiara with several tiers of bull horns, bull's ears at the "
          "sides, bust cut off at the shoulders, pale limestone, museum photograph, plain light grey background, soft even lighting, highly detailed, sharp focus")
NEG = "animal, lion, bull face, muzzle, snout, full body, cartoon, anime, text, watermark, blurry, multiple heads, colour, painted"


async def main():
    for n in range(1, 5):
        graph = await inv.create_text2img_graph(PROMPT, NEG, model_key=MODEL, width=832, height=1216, steps=35, cfg_scale=6.0, scheduler="dpmpp_2m")
        _, name = await inv._run_graph(graph)
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.get(f"{inv.INVOKEAI_BASE_URL}/api/v1/images/i/{name}/full")
        (OUT / f"lamassu_head_{n}.png").write_bytes(r.content)
        print(n, name, flush=True)


asyncio.run(main())
