"""
Build ANALYSIS-charts-embedded.md — a single self-contained copy of ANALYSIS.md with
every chart inlined as a data URI, so the file can be mailed, dropped in a Drive folder
or opened on its own and the charts still show.

The repo copy (ANALYSIS.md) keeps ordinary relative links to charts/*.svg, which is what
GitHub renders. GitHub sanitises data URIs out of markdown, so the two copies exist for
two different destinations and neither one covers both.

Charts are inlined as SVG rather than rasterised PNG: they stay vector (sharp at any
zoom), they carry the light/dark media query with them, and the whole file lands around
80KB instead of 400KB. The cost is that a markdown viewer with aggressive SVG
sanitisation will show nothing — open it in a browser if that happens.

    python3 embed_charts.py        # ANALYSIS.md -> ANALYSIS-charts-embedded.md
"""
import base64
import os
import re

SRC = "ANALYSIS.md"
DST = "ANALYSIS-charts-embedded.md"

PREAMBLE_FROM = "Data pulled 13 Aug 2026. Sources and reproduction steps in [§10](#10-how-to-verify)."
PREAMBLE_TO = (
    "Data pulled 13 Aug 2026. Sources and reproduction steps in [§10](#10-how-to-verify).\n\n"
    "*Charts are embedded directly in this file — open it anywhere, on its own, and they "
    "show. The repo copy `ANALYSIS.md` links to `charts/*.svg` instead, because GitHub "
    "strips embedded images. Regenerate this file with `python3 embed_charts.py`.*"
)


def inline(match):
    alt, path = match.group(1), match.group(2)
    if not os.path.exists(path):
        raise SystemExit(f"missing chart: {path}")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"![{alt}](data:image/svg+xml;base64,{b64})"


def main():
    doc = open(SRC).read()
    if PREAMBLE_FROM not in doc:
        raise SystemExit(f"{SRC}: preamble anchor not found, cannot place the note")
    doc = doc.replace(PREAMBLE_FROM, PREAMBLE_TO, 1)
    doc, n = re.subn(r"!\[([^\]]*)\]\((charts/[^)]+\.svg)\)", inline, doc)
    with open(DST, "w") as f:
        f.write(doc)
    print(f"wrote {DST}  ({n} charts inlined, {os.path.getsize(DST)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
