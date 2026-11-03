"""The legends of the disk that are laid as clay tablets in the world (see research/LEGENDS.md).

slug     - prefix of the place ids, models and knowledge cards: <slug>_tablet_<n>
count    - number of tablets (episodes) of the legend
sign     - the key sign written on the first line of each tablet (a Unicode cuneiform code point); the second line holds
           as many strokes as the number of the tablet
An optional `signature` (code points) is written in the last register, right-aligned: the author's name on the disclaimer tablet,
PI TE ISH, wi-te-is, Vitex as near as the syllabary comes (an easter egg, nothing in the cards points at it).
Not scribal numbering: none of these legends is divided into numbered tablets in the sources the disk uses, except the
Standard Babylonian Gilgamesh (twelve); the strokes only tell the tablets of one legend apart.
"""
LEGENDS = [
    {"slug": "gilgamesh_epic", "count": 12, "sign": 0x12217},  # LUGAL, king
    {"slug": "etana", "count": 3, "sign": 0x1202D},            # AN, heaven
    {"slug": "adapa", "count": 2, "sign": 0x12000},            # A, water
    {"slug": "dilmun", "count": 2, "sign": 0x121A0},           # KI, earth
    {"slug": "nergal", "count": 2, "sign": 0x121B3},           # KUR, the land below
    {"slug": "disclaimer", "count": 1, "sign": 0x12097, "signature": [0x1227F, 0x122FC, 0x12156]},        # EN, lord (Enki): the author's disclaimer tablet; signature PI TE ISH = wi-te-is, "Vitex" in sound
]
