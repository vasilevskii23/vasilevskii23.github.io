#!/usr/bin/env python3
"""Generate Instagram story stats card: views, dates, circular portrait."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
ORIG = ROOT / "assets" / "story-original.jpg"
PORTRAIT = ROOT / "assets" / "portrait-new.jpg"
FONT_NUM = ROOT / "fonts" / "Oswald-Bold.ttf"
FONT_LABEL = ROOT / "fonts" / "Roboto-Bold.ttf"
FONT_MONO = ROOT / "fonts" / "JetBrainsMono-Regular.ttf"
OUT_JPG = ROOT / "story-views-3.5mln.jpg"
OUT_PNG = ROOT / "output" / "story-views-updated.png"


def rounded_rect_mask(w: int, h: int, radius: int, inset: int = 0) -> np.ndarray:
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([inset, inset, w - 1 - inset, h - 1 - inset], radius=radius, fill=255)
    return np.array(m) > 128


def main() -> None:
    orig = Image.open(ORIG).convert("RGB")
    w, h = orig.size
    og = np.array(orig)
    gray = np.array(orig.convert("L"))

    logo_mask = (gray > 160) & (np.arange(h)[:, None] < 220) & (np.arange(w)[None, :] < 280)
    logo_mask = ndimage.binary_dilation(logo_mask, iterations=2)

    inner = rounded_rect_mask(w, h, radius=36, inset=10)
    rng = np.random.default_rng(7)
    grain = np.clip(rng.normal(2.0, 3.8, (h, w, 3)), 0, 20).astype(np.uint8)

    new_arr = og.copy()
    new_arr[inner] = grain[inner]
    new_arr[logo_mask] = og[logo_mask]
    im = Image.fromarray(new_arr)

    cx, cy, r = 654, 212, 202
    portrait = Image.open(PORTRAIT).convert("L")
    portrait = ImageEnhance.Contrast(portrait).enhance(1.22)
    portrait = ImageEnhance.Brightness(portrait).enhance(1.0).convert("RGB")
    side = r * 2
    pw, ph = portrait.size
    scale = max(side / pw, side / ph) * 1.28
    nw, nh = int(pw * scale), int(ph * scale)
    portrait = portrait.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - side) // 2
    top = max(0, int((nh - side) * 0.20))
    if top + side > nh:
        top = nh - side
    portrait = portrait.crop((left, top, left + side, top + side))

    mask_hi = Image.new("L", (side * 4, side * 4), 0)
    ImageDraw.Draw(mask_hi).ellipse([1, 1, side * 4 - 2, side * 4 - 2], fill=255)
    mask = mask_hi.resize((side, side), Image.Resampling.LANCZOS)
    im.paste(portrait, (cx - r, cy - r), mask)

    draw = ImageDraw.Draw(im)
    font_label = ImageFont.truetype(str(FONT_LABEL), 32)
    font_num = ImageFont.truetype(str(FONT_NUM), 141)
    font_mono = ImageFont.truetype(str(FONT_MONO), 28)

    label = "ПРОСМОТРЫ"
    bb = draw.textbbox((0, 0), label, font=font_label)
    draw.text((117, 433 - bb[1]), label, font=font_label, fill=(255, 255, 255))

    text = "3,5 млн"
    bb = draw.textbbox((0, 0), text, font=font_num)
    draw.text((117, 521 - bb[1]), text, font=font_num, fill=(255, 255, 255))

    for t, y in [("30 ДНЕЙ", 940), ("16.09 — 15.10", 992)]:
        bb = draw.textbbox((0, 0), t, font=font_mono)
        draw.text((117, y - bb[1]), t, font=font_mono, fill=(255, 255, 255))

    OUT_JPG.parent.mkdir(parents=True, exist_ok=True)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT_JPG, quality=97)
    im.save(OUT_PNG)
    print(f"Wrote {OUT_JPG}")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
