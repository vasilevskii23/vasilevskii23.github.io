#!/usr/bin/env python3
"""Grade a motion-blurred night photo toward a long-exposure reference look."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
SRC_PATH = ROOT / "input" / "source.jpg"
REF_PATH = ROOT / "input" / "reference.jpg"
OUT_DIR = ROOT / "output"


def load_bgr(path: Path) -> np.ndarray:
    pil = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def save_bgr(path: Path, bgr: np.ndarray, quality: int = 92) -> None:
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    Image.fromarray(rgb).save(path, quality=quality, optimize=True)


def crop_reference_content(ref: np.ndarray) -> np.ndarray:
    h, w = ref.shape[:2]
    return ref[int(h * 0.07) : int(h * 0.93), :]


def match_histogram_channel(source: np.ndarray, reference: np.ndarray) -> np.ndarray:
    src = source.ravel()
    ref = reference.ravel()
    src_values, src_idx, src_counts = np.unique(src, return_inverse=True, return_counts=True)
    ref_values, ref_counts = np.unique(ref, return_counts=True)
    src_cdf = np.cumsum(src_counts).astype(np.float64)
    src_cdf /= src_cdf[-1]
    ref_cdf = np.cumsum(ref_counts).astype(np.float64)
    ref_cdf /= ref_cdf[-1]
    interp = np.interp(src_cdf, ref_cdf, ref_values)
    return interp[src_idx].reshape(source.shape).astype(source.dtype)


def soft_lab_match(src_bgr: np.ndarray, ref_bgr: np.ndarray, mix: float = 0.72) -> np.ndarray:
    """Partial LAB histogram match so source color identity remains."""
    src_lab = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2LAB)
    ref_lab = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2LAB)
    matched = np.empty_like(src_lab)
    for c in range(3):
        matched[..., c] = match_histogram_channel(src_lab[..., c], ref_lab[..., c])
    blended = cv2.addWeighted(matched, mix, src_lab, 1.0 - mix, 0)
    return cv2.cvtColor(blended, cv2.COLOR_LAB2BGR)


def guided_sharpen(bgr: np.ndarray) -> np.ndarray:
    """Edge-aware sharpen: unsharp + bilateral cleanup, no deconvolution ringing."""
    denoise = cv2.bilateralFilter(bgr, d=7, sigmaColor=35, sigmaSpace=7)
    blur = cv2.GaussianBlur(denoise, (0, 0), 1.8)
    sharp = cv2.addWeighted(denoise, 1.55, blur, -0.55, 0)
    # Very light high-pass for trail definition
    gray = cv2.cvtColor(sharp, cv2.COLOR_BGR2GRAY).astype(np.float32)
    hp = gray - cv2.GaussianBlur(gray, (0, 0), 3.5)
    out = sharp.astype(np.float32)
    out += 0.22 * hp[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


def night_curve(bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    l = lab[..., 0] / 255.0
    # Gentle S-curve: deeper night, keep trail sparkle
    y = np.power(np.clip(l, 0, 1), 1.12)
    y = 1.08 * y - 0.03
    y = np.clip(y, 0, 1)
    # Soft shoulder
    hi = np.clip((y - 0.82) / 0.18, 0, 1)
    y = y * (1 - 0.25 * hi) + (0.82 + 0.18 * np.sqrt(np.clip((y - 0.82) / 0.18, 0, 1))) * hi
    lab[..., 0] = np.clip(y * 255.0, 0, 255)
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


def teal_orange_grade(bgr: np.ndarray) -> np.ndarray:
    """Reference palette: warm gold architecture lights + cyan traffic trails."""
    img = bgr.astype(np.float32) / 255.0
    b, g, r = cv2.split(img)
    lum = 0.114 * b + 0.587 * g + 0.299 * r

    warm = np.clip((r - b) * 2.4 + (r - g) * 1.1, 0, 1)
    cool = np.clip((b - r) * 2.3 + (g - r) * 0.35, 0, 1)

    # Gold lift in warm bright zones
    r = np.clip(r + 0.14 * warm * np.clip(lum + 0.15, 0, 1), 0, 1)
    g = np.clip(g + 0.07 * warm * np.clip(lum + 0.1, 0, 1), 0, 1)
    b = np.clip(b - 0.08 * warm * lum, 0, 1)

    # Cyan/electric blue in cool streaks
    b = np.clip(b + 0.16 * cool, 0, 1)
    g = np.clip(g + 0.07 * cool, 0, 1)
    r = np.clip(r - 0.07 * cool, 0, 1)

    # Shadows cooler / deeper navy
    shadow = np.clip(1.0 - lum * 1.6, 0, 1)
    b = np.clip(b + 0.04 * shadow, 0, 1)
    r = np.clip(r - 0.025 * shadow, 0, 1)

    # Overall night saturation
    mean = (r + g + b) / 3.0
    sat = 1.18
    r = np.clip(mean + (r - mean) * sat, 0, 1)
    g = np.clip(mean + (g - mean) * sat, 0, 1)
    b = np.clip(mean + (b - mean) * sat, 0, 1)

    return (cv2.merge([b, g, r]) * 255.0).astype(np.uint8)


def enhance_trails(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = cv2.split(hsv)
    bright = np.clip((v - 110.0) / 90.0, 0, 1)

    # Soft bloom on lights
    bloom = cv2.GaussianBlur((v * bright).astype(np.uint8), (0, 0), 9).astype(np.float32)
    v = np.clip(v + 0.22 * bloom, 0, 255)

    # Mild directional streak (horizontal urban traffic feel)
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    streak = cv2.morphologyEx((v * bright).astype(np.uint8), cv2.MORPH_CLOSE, k).astype(np.float32)
    v = np.clip(v + 0.10 * streak * bright, 0, 255)

    s = np.clip(s + 22.0 * bright, 0, 255)
    return cv2.cvtColor(cv2.merge([h, s, v]).astype(np.uint8), cv2.COLOR_HSV2BGR)


def wet_asphalt_contrast(bgr: np.ndarray) -> np.ndarray:
    """Deepen dark road-like regions while keeping specular highlights."""
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    l = lab[..., 0]
    dark = np.clip((95.0 - l) / 95.0, 0, 1)
    l = l - 18.0 * dark + 6.0 * (1.0 - dark) * np.clip((l - 160) / 80.0, 0, 1)
    lab[..., 0] = np.clip(l, 0, 255)
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)


def vignette(bgr: np.ndarray, strength: float = 0.32) -> np.ndarray:
    h, w = bgr.shape[:2]
    y, x = np.ogrid[:h, :w]
    cy, cx = h / 2.0, w / 2.0
    dist = np.sqrt(((x - cx) / (cx * 1.05)) ** 2 + ((y - cy) / (cy * 1.05)) ** 2)
    mask = 1.0 - strength * np.clip(dist ** 1.45, 0, 1)
    return np.clip(bgr.astype(np.float32) * mask[..., None], 0, 255).astype(np.uint8)


def film_grain(bgr: np.ndarray, amount: float = 2.8) -> np.ndarray:
    noise = np.random.default_rng(7).normal(0, amount, bgr.shape[:2]).astype(np.float32)
    out = bgr.astype(np.float32)
    out += noise[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


def make_side_by_side(a: np.ndarray, b: np.ndarray, label_a: str, label_b: str) -> np.ndarray:
    h = 1600

    def fit(img: np.ndarray) -> np.ndarray:
        scale = h / img.shape[0]
        return cv2.resize(img, (int(img.shape[1] * scale), h), interpolation=cv2.INTER_AREA)

    left, right = fit(a), fit(b)
    max_w = max(left.shape[1], right.shape[1])

    def pad(img: np.ndarray) -> np.ndarray:
        if img.shape[1] == max_w:
            return img
        canvas = np.zeros((h, max_w, 3), dtype=np.uint8)
        x0 = (max_w - img.shape[1]) // 2
        canvas[:, x0 : x0 + img.shape[1]] = img
        return canvas

    left, right = pad(left), pad(right)
    combo = np.hstack([left, right])
    for text, x in ((label_a, 24), (label_b, max_w + 24)):
        cv2.putText(combo, text, (x, 48), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
    return combo


def process() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    src = load_bgr(SRC_PATH)
    ref = crop_reference_content(load_bgr(REF_PATH))

    # Slight exposure pull-down before grade (source is much brighter than night ref)
    exposed = cv2.convertScaleAbs(src, alpha=0.82, beta=-8)

    print("color match…")
    matched = soft_lab_match(exposed, ref, mix=0.68)
    print("sharpen…")
    sharp = guided_sharpen(matched)
    print("night grade…")
    toned = night_curve(sharp)
    graded = teal_orange_grade(toned)
    trails = enhance_trails(graded)
    asphalt = wet_asphalt_contrast(trails)
    vign = vignette(asphalt, strength=0.30)
    final = film_grain(vign, amount=2.6)

    # Align overall brightness closer to reference without flattening trails
    fl = cv2.cvtColor(final, cv2.COLOR_BGR2LAB).astype(np.float32)
    rl = cv2.cvtColor(ref, cv2.COLOR_BGR2LAB).astype(np.float32)
    scale = (0.65 * float(rl[..., 0].mean()) / max(float(fl[..., 0].mean()), 1.0)) + 0.35
    fl[..., 0] = np.clip(fl[..., 0] * scale, 0, 255)
    final = cv2.cvtColor(fl.astype(np.uint8), cv2.COLOR_LAB2BGR)

    out_full = OUT_DIR / "processed_full.jpg"
    out_web = OUT_DIR / "processed_web.jpg"
    out_cmp = OUT_DIR / "before_after.jpg"

    save_bgr(out_full, final, quality=93)
    web = final
    if max(web.shape[:2]) > 2400:
        s = 2400 / max(web.shape[:2])
        web = cv2.resize(web, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    save_bgr(out_web, web, quality=90)
    save_bgr(out_cmp, make_side_by_side(src, final, "Before", "After (ref grade)"), quality=88)

    # Also copy web result to artifacts path for walkthrough
    artifacts = Path("/opt/cursor/artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)
    save_bgr(artifacts / "processed_ref_grade.jpg", web, quality=90)
    save_bgr(artifacts / "before_after.jpg", make_side_by_side(src, final, "Before", "After (ref grade)"), quality=86)

    print("wrote", out_full)
    print("wrote", out_web)
    print("wrote", out_cmp)
    print("final size", final.shape[1], "x", final.shape[0])


if __name__ == "__main__":
    process()
