#!/usr/bin/env python3
"""Build promotional collage / product card for Красный Октябрь piano giveaway."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
PHOTOS = ROOT / "photos"
OUT = ROOT

W, H = 1080, 1350  # Instagram portrait / marketplace-friendly

TEXT = (
    "08.11.26 до 15:00 можно совершенно бесплатно забрать, "
    "исправно, центральный р-н СПб, 2й этаж, широкая лестница. "
    "После будет уничтожено. Кто готов спасти инструмент?!"
)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def load(name: str) -> Image.Image:
    return Image.open(PHOTOS / name).convert("RGB")


def cover_crop(img: Image.Image, tw: int, th: int, focus=(0.5, 0.45)) -> Image.Image:
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    cx, cy = int(nw * focus[0]), int(nh * focus[1])
    left = max(0, min(cx - tw // 2, nw - tw))
    top = max(0, min(cy - th // 2, nh - th))
    return img.crop((left, top, left + tw, top + th))


def rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, img.size[0], img.size[1]), radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text_shadow(draw, xy, text, font, fill, shadow=(0, 0, 0, 180), offset=2):
    x, y = xy
    draw.text((x + offset, y + offset), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def build() -> Image.Image:
    canvas = Image.new("RGB", (W, H), "#1a120c")
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Warm wood atmosphere background
    hero_blur = cover_crop(load("01-photo.jpg"), W, H, focus=(0.5, 0.4))
    hero_blur = hero_blur.filter(ImageFilter.GaussianBlur(28))
    hero_blur = ImageEnhance.Brightness(hero_blur).enhance(0.35)
    hero_blur = ImageEnhance.Color(hero_blur).enhance(0.7)
    canvas.paste(hero_blur, (0, 0))

    # Soft vignette
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(80):
        a = int(140 * (i / 80) ** 1.6)
        vd.rectangle((i, i, W - 1 - i, H - 1 - i), outline=(0, 0, 0, a))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), vignette).convert("RGB")
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Header bar
    draw.rectangle((0, 0, W, 118), fill=(26, 14, 10, 230))
    brand_font = ImageFont.truetype(FONT_SERIF, 42)
    sub_font = ImageFont.truetype(FONT_BOLD, 22)
    free_font = ImageFont.truetype(FONT_BOLD, 28)

    draw_text_shadow(draw, (40, 28), "КРАСНЫЙ ОКТЯБРЬ", brand_font, "#f0d9a8")
    draw.text((42, 78), "Пианино · Ленинградская фабрика", font=sub_font, fill="#b89a72")

    # FREE badge
    badge = "БЕСПЛАТНО"
    bw = int(draw.textlength(badge, font=free_font)) + 36
    bx, by = W - bw - 36, 34
    draw.rounded_rectangle((bx, by, bx + bw, by + 52), radius=10, fill="#c0392b")
    draw.text((bx + 18, by + 10), badge, font=free_font, fill="#fff8f0")

    # Main photo — user's piano
    main = rounded(cover_crop(load("01-photo.jpg"), 1000, 620, focus=(0.48, 0.42)), 18)
    canvas.paste(main, (40, 140), main)

    # Deadline strip over main photo bottom
    strip = Image.new("RGBA", (1000, 70), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip)
    for y in range(70):
        a = int(30 + 180 * (y / 70))
        sd.line([(0, y), (1000, y)], fill=(18, 10, 6, a))
    canvas.paste(strip, (40, 690), strip)
    dead_font = ImageFont.truetype(FONT_BOLD, 26)
    draw_text_shadow(
        draw,
        (58, 708),
        "08.11.26  ·  до 15:00  ·  Центральный р-н СПб",
        dead_font,
        "#fff4e0",
    )

    # Secondary collage row
    gap = 16
    thumb_w = (1000 - gap * 2) // 3
    thumb_h = 220
    thumbs = [
        ("01-photo.jpg", (0.55, 0.62)),  # keys close-up
        ("01-photo.jpg", (0.50, 0.32)),  # brand plaque / fallboard
        ("02-wiki-mahogany.jpg", (0.5, 0.45)),  # same brand, mahogany
    ]

    y0 = 780
    labels = ["Клавиатура", "Клеймо", "Та же марка"]
    lab_font = ImageFont.truetype(FONT_BOLD, 16)
    for i, ((name, focus), label) in enumerate(zip(thumbs, labels)):
        x = 40 + i * (thumb_w + gap)
        t = rounded(cover_crop(load(name), thumb_w, thumb_h, focus=focus), 14)
        canvas.paste(t, (x, y0), t)
        # label chip
        lw = int(draw.textlength(label, font=lab_font)) + 18
        draw.rounded_rectangle(
            (x + 10, y0 + thumb_h - 36, x + 10 + lw, y0 + thumb_h - 10),
            radius=8,
            fill=(20, 12, 8, 200),
        )
        draw.text((x + 19, y0 + thumb_h - 32), label, font=lab_font, fill="#f5e6c8")

    # Text panel
    panel_y = 1030
    draw.rounded_rectangle((40, panel_y, W - 40, H - 36), radius=18, fill=(28, 18, 12, 235))
    draw.rounded_rectangle((40, panel_y, W - 40, H - 36), radius=18, outline=(180, 140, 90, 90), width=2)

    title_font = ImageFont.truetype(FONT_BOLD, 30)
    body_font = ImageFont.truetype(FONT_REG, 24)
    draw.text((64, panel_y + 22), "Спасите инструмент!", font=title_font, fill="#f2d7a4")

    # accent line
    draw.rectangle((64, panel_y + 64, 220, panel_y + 68), fill="#c0392b")

    lines = wrap_text(draw, TEXT, body_font, W - 140)
    ty = panel_y + 84
    for line in lines:
        draw.text((64, ty), line, font=body_font, fill="#efe2cf")
        ty += 32

    # Footer urgency
    foot = ImageFont.truetype(FONT_BOLD, 18)
    draw.text((64, H - 70), "2-й этаж · широкая лестница · исправно", font=foot, fill="#c4a882")

    return canvas.convert("RGB")


def main() -> None:
    card = build()
    jpg = OUT / "krasny-oktyabr-card.jpg"
    png = OUT / "krasny-oktyabr-card.png"
    card.save(jpg, "JPEG", quality=92, optimize=True)
    card.save(png, "PNG", optimize=True)
    print(f"Wrote {jpg} ({jpg.stat().st_size} bytes)")
    print(f"Wrote {png} ({png.stat().st_size} bytes)")

    # Square feed variant with full announcement
    sq_img = build_square()
    sq = OUT / "krasny-oktyabr-collage-square.jpg"
    sq_img.save(sq, "JPEG", quality=92, optimize=True)
    print(f"Wrote {sq} ({sq.stat().st_size} bytes)")


def build_square() -> Image.Image:
    S = 1080
    canvas = Image.new("RGB", (S, S), "#1a120c")
    draw = ImageDraw.Draw(canvas, "RGBA")

    bg = cover_crop(load("01-photo.jpg"), S, S, focus=(0.5, 0.4))
    bg = bg.filter(ImageFilter.GaussianBlur(24))
    bg = ImageEnhance.Brightness(bg).enhance(0.32)
    canvas.paste(bg, (0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")

    brand_font = ImageFont.truetype(FONT_SERIF, 38)
    free_font = ImageFont.truetype(FONT_BOLD, 24)
    draw_text_shadow(draw, (36, 28), "КРАСНЫЙ ОКТЯБРЬ", brand_font, "#f0d9a8")
    bw = int(draw.textlength("БЕСПЛАТНО", font=free_font)) + 28
    draw.rounded_rectangle((S - bw - 32, 30, S - 32, 74), radius=9, fill="#c0392b")
    draw.text((S - bw - 18, 38), "БЕСПЛАТНО", font=free_font, fill="#fff8f0")

    main = rounded(cover_crop(load("01-photo.jpg"), 1008, 520, focus=(0.48, 0.42)), 16)
    canvas.paste(main, (36, 100), main)

    # two side thumbs
    tw, th = 496, 200
    t1 = rounded(cover_crop(load("01-photo.jpg"), tw, th, focus=(0.55, 0.62)), 12)
    t2 = rounded(cover_crop(load("02-wiki-mahogany.jpg"), tw, th, focus=(0.5, 0.45)), 12)
    canvas.paste(t1, (36, 640), t1)
    canvas.paste(t2, (36 + tw + 16, 640), t2)

    draw.rounded_rectangle((36, 860, S - 36, S - 36), radius=16, fill=(28, 18, 12, 235))
    title_font = ImageFont.truetype(FONT_BOLD, 26)
    body_font = ImageFont.truetype(FONT_REG, 22)
    draw.text((56, 880), "Спасите инструмент!  ·  до 15:00 08.11.26", font=title_font, fill="#f2d7a4")
    lines = wrap_text(draw, TEXT, body_font, S - 120)
    ty = 924
    for line in lines:
        draw.text((56, ty), line, font=body_font, fill="#efe2cf")
        ty += 28

    return canvas.convert("RGB")


if __name__ == "__main__":
    main()
