#!/bin/sh
# Rebuilds media/fonts/noto-sans-cuneiform-numerals.ttf: the two number signs of the memorial numerals
# (U+12079 DISH = 1, U+1230B U = 10) cut from Noto Sans Cuneiform (fonts-noto-core, OFL-1.1).
set -eu
cd "$(dirname "$0")/.."
python3 -m fontTools.subset /usr/share/fonts/truetype/noto/NotoSansCuneiform-Regular.ttf \
    --unicodes=U+12079,U+1230B,U+0020 --no-hinting --layout-features= \
    --output-file=media/fonts/noto-sans-cuneiform-numerals.ttf
