"""Rebuild the web versions of the FLUXS logo from the two originals.

Run from the repo root after replacing assets/img/logo/fluxs-square.png and
fluxs-wide.png (cream background, same layout):  python3 tools/make_logos.py
Needs Pillow and numpy.
"""
from collections import Counter

import numpy as np
from PIL import Image

D = "assets/img/logo/"


def colors(path, n=3):
    """Background (most common colour) and the n most common ink colours."""
    counts = Counter(Image.open(path).convert("RGB").getdata()).most_common()
    bg = np.array(counts[0][0], float)
    inks = [np.array(c, float) for c, _ in counts[1:] if np.linalg.norm(np.array(c) - bg) > 120][:n]
    return bg, inks


def transparent(path):
    """Unmix each pixel into (nearest ink, alpha) over the background."""
    bg, inks = colors(path)
    a = np.asarray(Image.open(path).convert("RGB"), float) - bg
    best_res = best_t = best_col = None
    for ink in inks:
        v = ink - bg
        t = np.clip((a @ v) / (v @ v), 0, 1)
        res = np.linalg.norm(a - t[..., None] * v, axis=-1)
        if best_res is None:
            best_res, best_t, best_col = res, t, np.broadcast_to(ink, a.shape).copy()
        else:
            m = res < best_res
            best_res[m], best_t[m], best_col[m] = res[m], t[m], ink
    return Image.fromarray(np.dstack([best_col, best_t * 255]).astype(np.uint8), "RGBA")


def trim(im):
    return im.crop(im.getbbox())


sq = transparent(D + "fluxs-square.png")
wd = transparent(D + "fluxs-wide.png")
sq.save(D + "fluxs-square-transparent.png")
wd.save(D + "fluxs-wide-transparent.png")

# Header: mark + FLUXS letters, without the tagline (unreadable at 40 px).
mark, letters = trim(wd.crop((0, 0, 820, 560))), trim(wd.crop((840, 0, 1960, 380)))
gap, h = 70, max(mark.height, letters.height)
hdr = Image.new("RGBA", (mark.width + gap + letters.width, h), (0, 0, 0, 0))
hdr.alpha_composite(mark, (0, (h - mark.height) // 2))
hdr.alpha_composite(letters, (mark.width + gap, (h - letters.height) // 2))
hdr.thumbnail((10000, 120), Image.LANCZOS)
hdr.save(D + "fluxs-header.png")

# Footer: wide logo with tagline, on its cream background.
foot = Image.open(D + "fluxs-wide.png").convert("RGB")
foot.thumbnail((640, 640), Image.LANCZOS)
foot.save(D + "fluxs-footer.png", optimize=True)

# Favicons: waves + cylinder only, centred on a square.
icon = trim(sq.crop((0, 0, 880, 520)))
s = max(icon.size) + 40
sqr = Image.new("RGBA", (s, s), (0, 0, 0, 0))
sqr.alpha_composite(icon, ((s - icon.width) // 2, (s - icon.height) // 2))
for n in (180, 32):
    sqr.resize((n, n), Image.LANCZOS).save(D + f"favicon-{n}.png")
bg, _ = colors(D + "fluxs-square.png")
touch = Image.new("RGBA", (s, s), tuple(int(c) for c in bg) + (255,))
touch.alpha_composite(sqr)
touch.resize((180, 180), Image.LANCZOS).convert("RGB").save(D + "apple-touch-icon.png")

print("ink colours:", ["#%02X%02X%02X" % tuple(int(x) for x in c) for c in colors(D + "fluxs-wide.png")[1]])
