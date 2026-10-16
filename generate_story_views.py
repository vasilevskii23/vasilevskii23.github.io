#!/usr/bin/env python3
"""Update story stats card: change number and dates only; keep original photo."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ORIG = ROOT / "assets" / "story-original.jpg"
FONT_NUM = ROOT / "fonts" / "Oswald-Bold.ttf"
FONT_MONO = ROOT / "fonts" / "JetBrainsMono-Regular.ttf"
OUT_JPG = ROOT / "story-views-3.5mln.jpg"
OUT_PNG = ROOT / "output" / "story-views-updated.png"

# Circular portrait in source — never modify this region
CX, CY, R = 654, 212, 202


def main() -> None:
    orig = Image.open(ORIG).convert("RGB")
    w, h = orig.size
    og = np.array(orig)
    yy, xx = np.ogrid[:h, :w]
    circle = (xx - CX) ** 2 + (yy - CY) ** 2 <= (R + 8) ** 2

    arr = og.copy()
    rng = np.random.default_rng(7)

    # Wipe old number (full glyph height) and old date line
    nx0, ny0, nx1, ny1 = 95, 500, 800, 780
    bg = og[800:920, 40:200]
    mean = bg.mean(axis=(0, 1))
    arr[ny0:ny1, nx0:nx1] = np.clip(
        rng.normal(mean, 3.2, size=(ny1 - ny0, nx1 - nx0, 3)), 0, 22
    ).astype(np.uint8)
    arr[circle] = og[circle]

    dx0, dy0, dx1, dy1 = 95, 980, 620, 1040
    bg2 = og[1050:1120, 40:180]
    mean2 = bg2.mean(axis=(0, 1))
    arr[dy0:dy1, dx0:dx1] = np.clip(
        rng.normal(mean2, 2.8, size=(dy1 - dy0, dx1 - dx0, 3)), 0, 22
    ).astype(np.uint8)

    im = Image.fromarray(arr)
    draw = ImageDraw.Draw(im)

    text = "3,5 млн"
    font_num = ImageFont.truetype(str(FONT_NUM), 141)
    bb = draw.textbbox((0, 0), text, font=font_num)
    draw.text((117, 521 - bb[1]), text, font=font_num, fill=(255, 255, 255))

    date_text = "16.09 — 15.10"
    font_date = ImageFont.truetype(str(FONT_MONO), 28)
    bb = draw.textbbox((0, 0), date_text, font=font_date)
    draw.text((117, 992 - bb[1]), date_text, font=font_date, fill=(255, 255, 255))

    OUT_JPG.parent.mkdir(parents=True, exist_ok=True)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT_JPG, quality=97)
    im.save(OUT_PNG)
    print(f"Wrote {OUT_JPG}")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
