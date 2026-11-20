#!/usr/bin/env python3
"""Muted cinematic grade inspired by Nolan (teal shadows, dusty warm highlights, grain)."""
import argparse
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

def grade(src: Image.Image) -> Image.Image:
    src = ImageOps.exif_transpose(src).convert("RGB")
    arr = np.asarray(src, dtype=np.float32) / 255.0
    r, g, b = arr[..., 0].copy(), arr[..., 1].copy(), arr[..., 2].copy()
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b

    sat = 0.50
    r = luma + (r - luma) * sat
    g = luma + (g - luma) * sat
    b = luma + (b - luma) * sat

    warm = np.clip((r - b) * 2.2, 0, 1) * np.clip((luma - 0.08) * 2.0, 0, 1)
    r = r - warm * 0.05
    g = g - warm * 0.01
    b = b + warm * 0.045

    sw = np.clip(1.0 - luma * 1.45, 0, 1) ** 1.15
    r = r + sw * (-0.045)
    g = g + sw * (0.012)
    b = b + sw * (0.075)

    mw = np.clip(1.0 - np.abs(luma - 0.38) * 2.4, 0, 1)
    r = r + mw * (-0.018)
    b = b + mw * (0.028)

    hi = np.clip((luma - 0.40) / 0.55, 0, 1) ** 1.25
    r = r + hi * (0.055)
    g = g + hi * (0.018)
    b = b + hi * (-0.028)

    x = np.clip(np.stack([r, g, b], axis=-1), 0, 1)
    x = x * 0.965 + 0.028 * np.array([0.03, 0.045, 0.07])
    x = (x - 0.47) * 1.30 + 0.47
    over = np.clip(x - 0.80, 0, None)
    x = np.clip(x - over * 0.35, 0, 1)

    img = Image.fromarray((x * 255).astype(np.uint8), "RGB")
    img = ImageEnhance.Color(img).enhance(0.90)
    img = ImageEnhance.Contrast(img).enhance(1.10)
    img = ImageEnhance.Brightness(img).enhance(0.93)

    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rx = (xx - w / 2) / (w * 0.72)
    ry = (yy - h / 2) / (h * 0.78)
    dist = np.sqrt(rx * rx + ry * ry)
    vig = 1.0 - np.clip((dist - 0.50) / 0.90, 0, 1) * 0.40
    arr2 = np.asarray(img, dtype=np.float32) * vig[..., None]
    img = Image.fromarray(np.clip(arr2, 0, 255).astype(np.uint8))

    rng = np.random.default_rng(11)
    grain = rng.normal(0, 7.5, size=(h, w, 1)).astype(np.float32)
    chroma = rng.normal(0, 1.8, size=(h, w, 3)).astype(np.float32)
    lum = np.asarray(img.convert("L"), dtype=np.float32) / 255.0
    gs = (1.2 - lum * 0.45)[..., None]
    arr3 = np.asarray(img, dtype=np.float32) + grain * gs + chroma * 0.5
    img = Image.fromarray(np.clip(arr3, 0, 255).astype(np.uint8))
    return img.filter(ImageFilter.UnsharpMask(radius=1.1, percent=60, threshold=3))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--quality", type=int, default=93)
    args = p.parse_args()
    out = grade(Image.open(args.input))
    out.save(args.output, "JPEG", quality=args.quality, optimize=True)

if __name__ == "__main__":
    main()
