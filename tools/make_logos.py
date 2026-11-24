"""Rebuild the derived web versions of the FLUXS logo from the SVG originals.

Originals (as provided, do not edit), in assets/img/logo/: fluxs-symbol.svg, fluxs-logo-horizontal.svg,
fluxs-logo-vertical.svg. favicon-32.png, favicon-180.png and /favicon.ico come from the designer's kit
(LOGOS/, also as provided) and are copied, not generated.
Generated here: fluxs-mark.svg (symbol trimmed to the drawing, for the header), apple-touch-icon.png and
fluxs-og.png (link previews), both on the cream background.
Run from the repo root on macOS (uses `sips` to rasterize):  python3 tools/make_logos.py   Needs Pillow.
"""
import re
import subprocess
import tempfile

from PIL import Image

D = "assets/img/logo/"
CREAM = (251, 248, 243)  # logo background colour


def raster(src, width):
    """SVG text -> RGBA PIL image `width` px wide (transparent background).

    sips draws an SVG at its own width/height and then rescales the bitmap, which blurs it, so we
    first rewrite width/height (keeping the viewBox) to the target size.
    """
    vb = [float(x) for x in re.search(r'viewBox="([^"]*)"', src).group(1).split()]
    height = round(width * vb[3] / vb[2])
    src = re.sub(r'(<svg[^>]*?) width="[^"]*" height="[^"]*"', rf'\1 width="{width}" height="{height}"', src, count=1)
    with tempfile.NamedTemporaryFile(suffix=".svg", mode="w") as s, tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        s.write(src)
        s.flush()
        subprocess.run(["sips", "-s", "format", "png", s.name, "--out", tmp.name], check=True, capture_output=True)
        return Image.open(tmp.name).convert("RGBA")


def on_cream(im, size):
    w, h = size
    out = Image.new("RGBA", (w, h), CREAM + (255,))
    out.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    return out.convert("RGB")


def fit(im, box):
    im = im.crop(im.getbbox())
    k = min(box / im.width, box / im.height)
    return im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)


# Header mark: the symbol with its viewBox trimmed to the drawing (the original is a padded square).
src = open(D + "fluxs-symbol.svg").read()
vb = [float(x) for x in re.search(r'viewBox="([^"]*)"', src).group(1).split()]
N = 2048
x0, y0, x1, y1 = raster(src, N).getbbox()
k = vb[2] / N
pad = 0.5
box = (vb[0] + x0 * k - pad, vb[1] + y0 * k - pad, (x1 - x0) * k + 2 * pad, (y1 - y0) * k + 2 * pad)
w = round(box[2] * 10)
h = round(box[3] * 10)
mark = re.sub(r'viewBox="[^"]*" width="[^"]*" height="[^"]*"',
              'viewBox="%.2f %.2f %.2f %.2f" width="%d" height="%d"' % (*box, w, h), src, count=1)
open(D + "fluxs-mark.svg", "w").write(mark)

# Apple touch icon: symbol on cream (iOS does not do transparency).
on_cream(fit(raster(src, 1024), 150), (180, 180)).save(D + "apple-touch-icon.png")

# Link previews (og:image): vertical logo on cream, 1200x1200.
on_cream(fit(raster(open(D + "fluxs-logo-vertical.svg").read(), 2048), 900), (1200, 1200)).save(D + "fluxs-og.png", optimize=True)
print("done", box)
