#!/usr/bin/env python3
"""Build a 5-slide creative Instagram carousel (1080×1350) from Lifotronic panda photos."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
FONTS = ROOT / "fonts"
OUT = ROOT / "slides"
ART = Path("/opt/cursor/artifacts/panda-carousel")

W, H = 1080, 1350
MARGIN = 56

PHOTOS = {
    "hero": ASSETS / "src-01-hero.jpg",
    "front": ASSETS / "src-02-front.jpg",
    "sidekid": ASSETS / "src-03-side.jpg",
    "profile": ASSETS / "src-04-profile.jpg",
    "rear": ASSETS / "src-05-rear.jpg",
}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / path), size)


def cover_crop(path: Path, size: tuple[int, int], focus=(0.5, 0.42)) -> Image.Image:
    im = Image.open(path).convert("RGB")
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    cx, cy = int(nw * focus[0]), int(nh * focus[1])
    left = max(0, min(nw - tw, cx - tw // 2))
    top = max(0, min(nh - th, cy - th // 2))
    return im.crop((left, top, left + tw, top + th))


def blur_frame(path: Path, size: tuple[int, int], focus=(0.5, 0.45)) -> Image.Image:
    """Fit the full photo into 4:5 over a blurred cover background."""
    tw, th = size
    src = Image.open(path).convert("RGB")
    bg = cover_crop(path, size, focus=focus)
    bg = bg.filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    # fit width
    scale = tw / src.width
    nw, nh = tw, int(src.height * scale)
    if nh > th - 80:
        scale = (th - 120) / src.height
        nw, nh = int(src.width * scale), int(src.height * scale)
    fg = src.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (tw - nw) // 2
    y = (th - nh) // 2
    bg.paste(fg, (x, y))
    return bg


def polish(im: Image.Image, contrast=1.08, color=1.06, sharp=1.2) -> Image.Image:
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(color)
    im = ImageEnhance.Sharpness(im).enhance(sharp)
    return im


def vignette(im: Image.Image, strength=160, soft=48) -> Image.Image:
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    inset = soft
    for i in range(inset):
        a = int(strength * ((i + 1) / inset) ** 1.8)
        d.rectangle([i, i, w - 1 - i, h - 1 - i], outline=a)
    mask = mask.filter(ImageFilter.GaussianBlur(soft))
    dark = Image.new("RGB", (w, h), (8, 6, 8))
    return Image.composite(dark, im, mask)


def bottom_fade(im: Image.Image, height=420, strength=210) -> Image.Image:
    w, h = im.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    y0 = h - height
    for y in range(height):
        a = int(strength * (y / (height - 1)) ** 1.35)
        d.line([(0, y0 + y), (w, y0 + y)], fill=(0, 0, 0, a))
    return Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")


def frame(im: Image.Image, pad=30, width=2) -> Image.Image:
    d = ImageDraw.Draw(im)
    d.rectangle([pad, pad, im.width - pad, im.height - pad], outline=(255, 255, 255), width=width)
    return im


def index_label(im: Image.Image, n: int, total: int = 5) -> Image.Image:
    d = ImageDraw.Draw(im)
    f = font("SpaceMono-Regular.ttf", 20)
    text = f"{n:02d} — {total:02d}"
    d.text((MARGIN, H - 58), text, fill=(0, 0, 0), font=f)
    d.text((MARGIN - 1, H - 59), text, fill=(255, 255, 255), font=f)
    return im


def text_shadow(draw, xy, text, font_, fill=(255, 255, 255), shadow=(0, 0, 0, 180)):
    x, y = xy
    for dx, dy in ((2, 2), (1, 1)):
        draw.text((x + dx, y + dy), text, font=font_, fill=shadow[:3])
    draw.text((x, y), text, font=font_, fill=fill)


def centered(draw, y, text, font_, fill=(255, 255, 255)):
    bbox = draw.textbbox((0, 0), text, font=font_)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    text_shadow(draw, (x, y), text, font_, fill=fill)
    return x, y, tw


def slide_01() -> Image.Image:
    # Hero: brand + pair programmer
    im = cover_crop(PHOTOS["hero"], (W, H), focus=(0.38, 0.42))
    im = polish(im)
    im = bottom_fade(im, 460, 225)
    im = vignette(im, 130, 40)
    d = ImageDraw.Draw(im)
    brand = font("Syne.ttf", 92)
    sub = font("SpaceMono-Regular.ttf", 26)
    centered(d, H - 220, "LIFOTRONIC", brand)
    # hairline
    bx = W // 2
    d.line([(bx - 70, H - 118), (bx + 70, H - 118)], fill=(255, 255, 255), width=2)
    centered(d, H - 102, "PAIR PROGRAMMER", sub)
    frame(im)
    return index_label(im, 1)


def slide_02() -> Image.Image:
    # Macro: eyes / hoodie / brand
    im = cover_crop(PHOTOS["front"], (W, H), focus=(0.62, 0.38))
    # tighter feel — crop center again toward face
    im = polish(im, 1.12, 1.08, 1.35)
    im = vignette(im, 150, 50)
    d = ImageDraw.Draw(im)
    tag = font("SpaceMono-Bold.ttf", 28)
    d.text((MARGIN + 2, MARGIN + 10), "DEBUG BUDDY", font=tag, fill=(0, 0, 0))
    d.text((MARGIN, MARGIN + 8), "DEBUG BUDDY", font=tag, fill=(255, 255, 255))
    note = font("InstrumentSerif-Italic.ttf", 36)
    text_shadow(d, (MARGIN, H - 190), "red hoodie. white drawstrings.", note)
    text_shadow(d, (MARGIN, H - 140), "serious about soft launches.", note)
    frame(im)
    return index_label(im, 2)


def slide_03() -> Image.Image:
    # Profile with vertical CODE — full scene via blur frame
    im = blur_frame(PHOTOS["profile"], (W, H), focus=(0.4, 0.5))
    im = polish(im, 1.08, 1.04, 1.2)
    im = bottom_fade(im, 260, 150)
    im = vignette(im, 120, 40)
    d = ImageDraw.Draw(im)
    big = font("InstrumentSerif-Regular.ttf", 92)
    letters = list("CODE")
    start_y = 300
    for i, ch in enumerate(letters):
        bbox = d.textbbox((0, 0), ch, font=big)
        tw = bbox[2] - bbox[0]
        x = W - MARGIN - tw - 4
        y = start_y + i * 120
        text_shadow(d, (x, y), ch, big)
    sub = font("SpaceMono-Regular.ttf", 22)
    text_shadow(d, (MARGIN, H - 120), "ship late. stay soft.", sub)
    frame(im)
    return index_label(im, 3)


def slide_04() -> Image.Image:
    # Watching the build / on call — full desk scene
    im = blur_frame(PHOTOS["rear"], (W, H), focus=(0.35, 0.45))
    im = polish(im)
    im = bottom_fade(im, 380, 210)
    im = vignette(im, 125, 40)
    d = ImageDraw.Draw(im)
    small = font("SpaceMono-Regular.ttf", 24)
    big = font("Syne.ttf", 64)
    centered(d, H - 210, "ON CALL", small)
    centered(d, H - 160, "watching the build", big)
    frame(im)
    return index_label(im, 4)


def slide_05() -> Image.Image:
    # Brand lockup closing
    im = cover_crop(PHOTOS["sidekid"], (W, H), focus=(0.45, 0.4))
    # Prefer a cleaner front if side has child - use front with different crop
    im = cover_crop(PHOTOS["front"], (W, H), focus=(0.55, 0.4))
    im = polish(im, 1.06, 1.04, 1.15)
    im = bottom_fade(im, 520, 230)
    # also top fade for lockup
    top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(top)
    for y in range(280):
        a = int(170 * (1 - y / 279) ** 1.2)
        td.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    im = Image.alpha_composite(im.convert("RGBA"), top).convert("RGB")
    im = vignette(im, 145, 46)
    d = ImageDraw.Draw(im)
    brand = font("Syne.ttf", 78)
    tag = font("InstrumentSerif-Italic.ttf", 34)
    # top lockup
    _, y, tw = centered(d, 86, "LIFOTRONIC", brand)
    bx = W // 2
    d.line([(bx - tw // 2, 78), (bx + tw // 2, 78)], fill=(255, 255, 255), width=2)
    d.line([(bx - tw // 2, 178), (bx + tw // 2, 178)], fill=(255, 255, 255), width=2)
    centered(d, 196, "Soft mascot. Serious tools.", tag)
    # bottom CTA-ish
    foot = font("SpaceMono-Regular.ttf", 22)
    centered(d, H - 110, "swipe for the whole desk", foot)
    frame(im)
    return index_label(im, 5)


def contact_sheet(slides: list[Image.Image]) -> Image.Image:
    gap = 20
    pw = W * len(slides) + gap * (len(slides) + 1)
    ph = H + gap * 2
    sheet = Image.new("RGB", (pw, ph), (14, 12, 16))
    x = gap
    for s in slides:
        sheet.paste(s, (x, gap))
        x += W + gap
    return sheet.resize((pw // 2, ph // 2), Image.Resampling.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    builders = [slide_01, slide_02, slide_03, slide_04, slide_05]
    slides = []
    for i, build in enumerate(builders, 1):
        im = build()
        path = OUT / f"carousel_{i:02d}.jpg"
        im.save(path, "JPEG", quality=93, optimize=True, progressive=True)
        im.save(ART / f"carousel_{i:02d}.jpg", "JPEG", quality=93, optimize=True)
        slides.append(im)
        print(f"wrote {path} ({path.stat().st_size} bytes)")
    preview = contact_sheet(slides)
    preview.save(OUT / "carousel_preview.jpg", "JPEG", quality=88, optimize=True)
    preview.save(ART / "carousel_preview.jpg", "JPEG", quality=88, optimize=True)
    print(f"preview {OUT / 'carousel_preview.jpg'}")


if __name__ == "__main__":
    main()
