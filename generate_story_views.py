#!/usr/bin/env python3
"""Update story stats: change number + dates only; keep original photo."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ORIG = ROOT / "assets" / "story-original.jpg"
FONT_NUM = ROOT / "fonts" / "Oswald-Bold.ttf"
FONT_DATE = ROOT / "fonts" / "SourceCodePro-Regular.ttf"
OUT_JPG = ROOT / "story-views-5.1mln.jpg"
OUT_PNG = ROOT / "output" / "story-views-updated.png"

CX, CY, R = 654, 212, 202


def main() -> None:
    orig = np.array(Image.open(ORIG).convert("RGB"))
    gray = cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    circle = (np.arange(w) - CX) ** 2 + (np.arange(h)[:, None] - CY) ** 2 <= (R + 8) ** 2

    num_band = np.zeros((h, w), dtype=bool)
    num_band[510:780, 105:775] = True
    date_band = np.zeros((h, w), dtype=bool)
    date_band[983:1040, 100:620] = True

    mask = np.zeros((h, w), dtype=np.uint8)
    mask[(gray > 30) & num_band & (~circle)] = 255
    mask[(gray > 30) & date_band] = 255
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)), iterations=3)
    mask[circle] = 0
    mask[900:980, :] = 0
    mask[:500, :] = 0

    bgr = cv2.cvtColor(orig, cv2.COLOR_RGB2BGR)
    inp = cv2.inpaint(bgr, mask, 8, cv2.INPAINT_TELEA)
    inp_rgb = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)

    rgb = orig.copy()
    rgb[mask > 0] = inp_rgb[mask > 0]
    rgb[circle] = orig[circle]
    rgb[900:980, :] = orig[900:980, :]
    rgb[:500, :] = orig[:500, :]

    nb = (gray > 180) & num_band & (~circle)
    ys, xs = np.where(nb)
    x0, y0 = int(xs.min()), int(ys.min())
    box_w, box_h = int(xs.max() - xs.min()) + 1, int(ys.max() - ys.min()) + 1

    text = "5,1 млн"
    scale = 6
    font = ImageFont.truetype(str(FONT_NUM), box_h * scale)
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=font)
    g = Image.new("L", (bb[2] - bb[0] + 8 * scale, bb[3] - bb[1] + 8 * scale), 0)
    ImageDraw.Draw(g).text((4 * scale - bb[0], 4 * scale - bb[1]), text, font=font, fill=255)
    g = g.resize((int(g.width * box_h / g.height), box_h), Image.Resampling.LANCZOS)
    if g.width > box_w:
        g = g.resize((box_w, box_h), Image.Resampling.LANCZOS)
    g = g.filter(ImageFilter.GaussianBlur(0.25))

    base = Image.fromarray(rgb).convert("RGBA")
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer = Image.new("RGBA", g.size, (252, 252, 252, 255))
    layer.putalpha(g)
    ov.paste(layer, (x0, y0), layer)
    base = Image.alpha_composite(base, ov)

    db = (
        (gray > 180)
        & (np.arange(h)[:, None] >= 988)
        & (np.arange(h)[:, None] <= 1030)
        & (np.arange(w)[None, :] >= 110)
        & (np.arange(w)[None, :] <= 580)
    )
    dys, dxs = np.where(db)
    d_left, d_top = int(dxs.min()), int(dys.min())
    d_h = int(dys.max() - dys.min()) + 1
    days = orig[940:962, 117:290]
    col = tuple(int(c) for c in days[days.mean(2) > 180].mean(0))
    date_text = "22.09 — 21.10"
    font = ImageFont.truetype(str(FONT_DATE), d_h * scale)
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), date_text, font=font)
    g = Image.new("L", (bb[2] - bb[0] + 4 * scale, bb[3] - bb[1] + 4 * scale), 0)
    ImageDraw.Draw(g).text((2 * scale - bb[0], 2 * scale - bb[1]), date_text, font=font, fill=255)
    g = g.resize((int(g.width * d_h / g.height), d_h), Image.Resampling.LANCZOS)
    g = g.filter(ImageFilter.GaussianBlur(0.2))

    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer = Image.new("RGBA", g.size, col + (255,))
    layer.putalpha(g)
    ov.paste(layer, (d_left, d_top), layer)
    im = Image.alpha_composite(base, ov).convert("RGB")

    OUT_JPG.parent.mkdir(parents=True, exist_ok=True)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT_JPG, quality=98)
    im.save(OUT_PNG)
    print(f"Wrote {OUT_JPG}")


if __name__ == "__main__":
    main()
