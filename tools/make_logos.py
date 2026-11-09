"""Rebuild the web versions of the FLUXS logo from the SVG originals.

Originals (as provided, do not edit): assets/img/logo/fluxs-symbol.svg,
fluxs-logo-compact.svg, fluxs-logo-horizontal.svg.
Also refreshes the LOGOS/ kit (SVG + PNG). Run from the repo root on macOS (uses `sips` to rasterize):  python3 tools/make_logos.py
Needs Pillow.
"""
import re
import subprocess
import tempfile

from PIL import Image

D = "assets/img/logo/"
CREAM = (251, 248, 243)  # logo background colour


def raster(svg, width):
    """SVG -> RGBA PIL image `width` px wide (transparent background).

    sips draws an SVG at its own width/height and then rescales the bitmap, which blurs it, so we
    first rewrite width/height (keeping the viewBox) to the target size in a temporary copy.
    """
    src = open(svg).read()
    vb = [float(x) for x in re.search(r'viewBox="([^"]*)"', src).group(1).split()]
    height = round(width * vb[3] / vb[2])
    src = re.sub(r'(<svg[^>]*?) width="[^"]*" height="[^"]*"', rf'\1 width="{width}" height="{height}"', src, count=1)
    with tempfile.NamedTemporaryFile(suffix=".svg", mode="w") as s, tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        s.write(src)
        s.flush()
        subprocess.run(["sips", "-s", "format", "png", s.name, "--out", tmp.name], check=True, capture_output=True)
        return Image.open(tmp.name).convert("RGBA")


def on_cream(im, pad=0, size=None):
    w, h = size or (im.width + 2 * pad, im.height + 2 * pad)
    out = Image.new("RGBA", (w, h), CREAM + (255,))
    out.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return out.convert("RGB")


# Header: horizontal logo with the viewBox trimmed to the drawing, so it fills the header height.
svg = open(D + "fluxs-logo-horizontal.svg").read()
svg = re.sub(r'viewBox="[^"]*" width="[^"]*" height="[^"]*"', 'viewBox="24 31 803 165" width="803" height="165"', svg, count=1)
open(D + "fluxs-header.svg", "w").write(svg)

# Favicons from the symbol, centred on a square.
sym = raster(D + "fluxs-symbol.svg", 1024)
sym = sym.crop(sym.getbbox())
s = int(max(sym.size) * 1.08)
sq = Image.new("RGBA", (s, s), (0, 0, 0, 0))
sq.alpha_composite(sym, ((s - sym.width) // 2, (s - sym.height) // 2))
for n in (32, 180):
    sq.resize((n, n), Image.LANCZOS).save(D + f"favicon-{n}.png")
on_cream(sq.resize((150, 150), Image.LANCZOS), size=(180, 180)).save(D + "apple-touch-icon.png")

# Link previews (og:image) and search engines: compact logo on cream, 1200x1200.
comp = raster(D + "fluxs-logo-compact.svg", 900)
on_cream(comp, size=(1200, 1200)).save(D + "fluxs-og.png", optimize=True)
# LOGOS/: logo kit for people outside the site (slides, posters, documents).
# SVG originals plus PNG renders, transparent and on the cream background.
import os
import shutil

K = "LOGOS/"
os.makedirs(K, exist_ok=True)
for name, width in (("fluxs-symbol", 1600), ("fluxs-logo-compact", 1600), ("fluxs-logo-horizontal", 3000)):
    shutil.copyfile(D + name + ".svg", K + name + ".svg")
    im = raster(D + name + ".svg", width)
    im.save(K + name + "-transparent.png", optimize=True)
    on_cream(im).save(K + name + "-cream.png", optimize=True)
print("done")
