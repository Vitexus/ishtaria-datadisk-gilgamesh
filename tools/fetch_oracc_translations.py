#!/usr/bin/env python3
"""Fetch English translations of ORACC texts, politely and resumably.

ORACC's JSON packages (https://oracc.museum.upenn.edu/json/<project>.zip) contain only the
lemmatised transliteration and search indexes, not the translation text.  The translation is
served by the documented simple HTML view ``/<project>/<Pnumber>/html``; this script reads the
list of translated texts from the package metadata and fetches that view for each of them,
one request every ``--delay`` seconds, appending results to a JSON-lines file.  Already
fetched texts are skipped, so an interrupted run can simply be started again.

    python3 -I tools/fetch_oracc_translations.py WORKDIR PROJECT [PROJECT ...]

WORKDIR must contain ``<project-with-dashes>.zip`` (downloaded from the URL above).  Because
oracc.museum.upenn.edu does not send its intermediate certificate, pass the CA bundle with
the missing InCommon RSA Server CA 2 certificate appended in ``ORACC_CA_BUNDLE``.

Licence of the data: Creative Commons Attribution-ShareAlike 3.0 (ORACC and the individual
projects); keep the project and author attribution when quoting.
"""
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

DELAY = 0.7
UA = "ishtaria-research-fetch/1.0 (open data, 1 request per second)"


def tr_texts(page: str):
    return [
        re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m))).strip()
        for m in re.findall(r'<p class="tr">(.*?)</p>', page, flags=re.S)
    ]


def main(workdir: str, projects: list[str]) -> None:
    work = Path(workdir)
    ctx = ssl.create_default_context(cafile=os.environ.get("ORACC_CA_BUNDLE") or None)
    for project in projects:
        dashed = project.replace("/", "-")
        out_path = work / f"tr_{dashed}.jsonl"
        done = set()
        if out_path.exists():
            done = {json.loads(line)["p"] for line in open(out_path, encoding="utf-8")}
        with zipfile.ZipFile(work / f"{dashed}.zip") as z:
            meta = json.loads(z.read(f"{project}/metadata.json"))
            try:
                cat = json.loads(z.read(f"{project}/catalogue.json")).get("members", {})
            except KeyError:
                cat = {}
        todo = [p for p in meta["formats"].get("tr-en", []) if p not in done]
        print(f"{project}: {len(todo)} to fetch ({len(done)} done)", flush=True)
        with open(out_path, "a", encoding="utf-8") as out:
            for n, pid in enumerate(todo, 1):
                url = f"https://oracc.museum.upenn.edu/{project}/{pid}/html"
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": UA})
                    page = urllib.request.urlopen(req, timeout=60, context=ctx).read().decode("utf-8")
                except Exception as exc:  # network hiccup: skip, a rerun retries it
                    print("  failed", pid, exc, flush=True)
                    time.sleep(5)
                    continue
                title = re.search(r'<h1[^>]*class="p3h2[^"]*"[^>]*>(.*?)</h1>', page, flags=re.S)
                heading = html.unescape(re.sub(r"<[^>]+>", " ", title.group(1))) if title else ""
                heading = re.sub(r"\s+", " ", re.sub(r"\[via [^\]]*\]", "", heading)).strip()
                row = {"p": pid, "project": project, "designation": heading,
                       "tr": tr_texts(page)}
                for key in ("period", "provenience", "genre", "date_of_origin", "language", "author"):
                    if key in cat.get(pid, {}):
                        row[key] = cat[pid][key]
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                out.flush()
                if n % 50 == 0:
                    print(f"  {project}: {n}/{len(todo)}", flush=True)
                time.sleep(DELAY)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
