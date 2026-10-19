#!/usr/bin/env python3
"""Corrected concept images (crowd_<id>_2.png) for crowd figures that Rodin mangled.

    python3 models-src/rodin/make_crowd_fix_concepts.py [id ...]

Same model, sampler, style and prompts as make_crowd_concepts.py (edit the prompts
there); the seed is offset by 1000 so a fix pass gets a fresh image. Defaults to the
two known fixes: crowd_archer (deformed bow merged into the body) and
crowd_pregnant_woman (read as holding a baby, plus a flesh-coloured blob at her feet).
"""
import asyncio
import os
import pathlib
import sys

os.environ["INVOKEAI_BASE_URL"] = os.environ.get("INVOKEAI_BASE_URL", "http://127.0.0.1:9090")
sys.path.insert(0, os.path.expanduser("~/Projects/Packaging/mcp-server-invokeai"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import httpx  # noqa: E402
import invokeai_mcp_server as inv  # noqa: E402
from make_crowd_concepts import CHARS, MODEL, NEG, OUT, STYLE  # noqa: E402


async def main():
    for npc in sys.argv[1:] or ["crowd_archer", "crowd_pregnant_woman"]:
        path = OUT / f"{npc}_2.png"
        if path.exists():
            print(f"skip {npc} (exists)", flush=True)
            continue
        graph = await inv.create_text2img_graph(f"{CHARS[npc]}, {STYLE}", NEG, model_key=MODEL,
                                                width=832, height=1216, steps=35, cfg_scale=6.0,
                                                scheduler="dpmpp_2m", seed=3000 + list(CHARS).index(npc))
        _, name = await inv._run_graph(graph)
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.get(f"{inv.INVOKEAI_BASE_URL}/api/v1/images/i/{name}/full")
        path.write_bytes(r.content)
        print(f"{npc} {name} -> {path.name} ({len(r.content)} bytes)", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
