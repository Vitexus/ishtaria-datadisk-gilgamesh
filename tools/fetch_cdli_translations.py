#!/usr/bin/env python3
"""Download the CDLI bulk dump and extract every tablet that has an English translation.

Writes one JSON object per line (id, period, genre, provenience, publication, translation
lines) to the output file.  Used for research/EVERYDAY_LIFE_SOURCES.md; the output (about
6 MB) is NOT committed - regenerate it with this script.

    python3 -I tools/fetch_cdli_translations.py /tmp/cdli-work translated.jsonl

Data: https://github.com/cdli-gh/data (git-lfs files, last dump August 2022).
"""
import csv
import json
import re
import sys
import urllib.request
from pathlib import Path

BASE = "https://media.githubusercontent.com/media/cdli-gh/data/master/"
FILES = ("cdliatf_unblocked.atf", "cdli_cat.csv")
KEEP = ("period", "genre", "subgenre", "provenience", "primary_publication",
        "designation", "date_of_origin", "language", "translation_source")


def main(workdir: str, out_name: str) -> None:
    work = Path(workdir)
    work.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        target = work / name
        if not target.exists():
            print("downloading", name)
            urllib.request.urlretrieve(BASE + name, target)

    csv.field_size_limit(10**9)
    catalogue = {}
    with open(work / "cdli_cat.csv", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            ident = row.get("id_text") or row.get("id")
            catalogue["P" + ident.zfill(6)] = {k: row.get(k, "") for k in KEEP}

    count = 0
    current, header, lines = None, "", []
    with open(work / out_name, "w", encoding="utf-8") as out:
        def flush():
            nonlocal count
            if current and lines:
                record = {"p": current, "hdr": header, **catalogue.get(current, {}), "tr": lines}
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1

        for raw in open(work / "cdliatf_unblocked.atf", encoding="utf-8"):
            line = raw.rstrip("\n")
            if line.startswith("&P"):
                flush()
                current, header, lines = line[1:8], line, []
            elif line.startswith("#tr.en"):
                lines.append(re.sub(r"^#tr\.en:\s*", "", line))
        flush()
    print(count, "tablets with an English translation ->", work / out_name)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
