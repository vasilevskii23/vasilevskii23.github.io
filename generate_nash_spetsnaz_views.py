#!/usr/bin/env python3
"""Compose НАШ СПЕЦНАЗ story card: raised original logo + 13,5 mln stats on bullet-hole wall."""

from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent
ORIG = ROOT / "assets" / "nash-spetsnaz-original.jpg"
WALL = ROOT / "assets" / "bullet-hole-wall-bg.jpg"
STATS = ROOT / "assets" / "stats-only-spetsnaz-font.jpg"
OUT_ROOT = ROOT / "nash-spetsnaz-13-5mln.jpg"
OUT_ASSETS = ROOT / "assets" / "nash-spetsnaz-13-5mln.jpg"
OUT_OUTPUT = ROOT / "output" / "nash-spetsnaz-13-5mln.jpg"

W, H = 1080, 1350


def extract_logo_flood(orig: Image.Image) -> Image.Image:
    crop = orig.crop((60, 340, 830, 575)).convert("RGBA")
    arr = np.array(crop)
    h, w = arr.shape[:2]
    lum = arr[:, :, :3].mean(axis=2)
    flooded = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            if lum[y, x] < 22:
                flooded[y, x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if lum[y, x] < 22 and not flooded[y, x]:
                flooded[y, x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not flooded[ny, nx] and lum[ny, nx] < 28:
                flooded[ny, nx] = True
                q.append((nx, ny))
    alpha = np.where(flooded, 0, 255).astype(np.uint8)
    soft = np.array(Image.fromarray(alpha, "L").filter(ImageFilter.GaussianBlur(0.55)))
    alpha = np.where(flooded, soft, 255).astype(np.uint8)
    arr[:, :, 3] = alpha
    ys, xs = np.where(alpha > 12)
    pad = 2
    return Image.fromarray(arr, "RGBA").crop(
        (
            max(0, xs.min() - pad),
            max(0, ys.min() - pad),
            min(w, xs.max() + pad),
            min(h, ys.max() + pad),
        )
    )


def key_stats(img: Image.Image) -> Image.Image:
    arr = np.array(img.convert("RGBA"))
    lum = arr[:, :, :3].mean(axis=2)
    alpha = np.clip((lum - 25) / 140 * 255, 0, 255)
    alpha[lum < 25] = 0
    alpha[lum > 170] = 255
    arr[:, :, 3] = alpha.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def paste_c(base: Image.Image, ov: Image.Image, y: int) -> int:
    x = (base.width - ov.width) // 2
    base.alpha_composite(ov, (x, y))
    return y + ov.height


def main() -> None:
    if not WALL.exists() or not STATS.exists():
        raise SystemExit(
            "Missing generated plates. Expected assets/bullet-hole-wall-bg.jpg "
            "and assets/stats-only-spetsnaz-font.jpg"
        )

    bg = Image.open(WALL).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    bg = ImageEnhance.Brightness(bg).enhance(0.72)
    bg = ImageEnhance.Contrast(bg).enhance(1.28)
    canvas = bg.convert("RGBA")

    logo = extract_logo_flood(Image.open(ORIG))
    tw = int(W * 0.90)
    logo = logo.resize((tw, int(logo.height * tw / logo.width)), Image.Resampling.LANCZOS)
    logo_y = 32
    paste_c(canvas, logo, logo_y)

    stats = key_stats(Image.open(STATS))
    a = np.array(stats)[:, :, 3]
    ys, xs = np.where(a > 12)
    stats = stats.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    avail_h = H - (logo_y + logo.height) - 70
    avail_w = int(W * 0.92)
    scale = min(avail_w / stats.width, avail_h / stats.height)
    stats = stats.resize(
        (int(stats.width * scale), int(stats.height * scale)), Image.Resampling.LANCZOS
    )
    paste_c(canvas, stats, logo_y + logo.height + 40)

    out = canvas.convert("RGB")
    OUT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    for path in (OUT_ROOT, OUT_ASSETS, OUT_OUTPUT):
        out.save(path, quality=97, optimize=True)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
