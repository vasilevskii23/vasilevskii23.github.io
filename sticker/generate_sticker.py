#!/usr/bin/env python3
"""Generate circular door sticker mockups for КРУЖИМ."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "logo.jpg"
QR = ROOT / "qr.png"
FONT_DISPLAY = ROOT / "fonts" / "Unbounded.ttf"
FONT_TEXT = ROOT / "fonts" / "GolosText.ttf"

OUT_STICKER = ROOT / "sticker.png"
OUT_TRANSPARENT = ROOT / "sticker_transparent.png"
OUT_DOOR = ROOT / "door_preview.png"
OUT_PRINT = ROOT / "sticker_print_300dpi.png"
OUT_DARK = ROOT / "sticker_dark.png"
OUT_DARK_PRINT = ROOT / "sticker_dark_transparent.png"

# Brand tokens from kruzhim.ru
BLUE_DEEP = (26, 58, 143, 255)      # --bd #1A3A8F
BLUE_MID = (41, 104, 212, 255)      # --bm #2968D4
ORANGE = (244, 98, 31, 255)         # --or #F4621F
RED_ORANGE = (224, 52, 26, 255)     # --ro #E0341A
INK = (13, 31, 92, 255)             # --ink #0D1F5C
WHITE = (255, 255, 255, 255)
LIGHT = (245, 248, 255, 255)        # text on dark / transparent variants
SKY = (95, 179, 255, 255)           # --bs #5FB3FF

SIZE = 2000


def circle_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def load_font(path: Path, size: int, weight: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(path), size)
    try:
        font.set_variation_by_axes([weight])
    except Exception:
        pass
    return font


def prep_logo(target: int) -> Image.Image:
    logo = Image.open(LOGO).convert("RGBA")
    w, h = logo.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    logo = logo.crop((left, top, left + side, top + side))
    logo = logo.resize((target, target), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (target, target), (0, 0, 0, 0))
    out.paste(logo, (0, 0), circle_mask(target))
    return out


def prep_qr(target: int) -> Image.Image:
    qr = Image.open(QR).convert("RGBA")
    # Crisp nearest-neighbor upscale for modules
    qr = qr.resize((target, target), Image.Resampling.NEAREST)
    # Soft rounded frame in brand orange (Yandex-pin energy, brand accent)
    pad = max(8, target // 18)
    frame = target + pad * 2
    canvas = Image.new("RGBA", (frame, frame), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    radius = max(12, frame // 12)
    draw.rounded_rectangle((0, 0, frame - 1, frame - 1), radius=radius, fill=ORANGE)
    inner = Image.new("RGBA", (target + pad, target + pad), WHITE)
    inset = pad // 2
    canvas.paste(inner, (inset, inset))
    canvas.paste(qr, (pad, pad), qr)
    return canvas


def draw_sticker(
    size: int = SIZE,
    shadow: bool = True,
    *,
    dark: bool = False,
    transparent: bool = False,
) -> Image.Image:
    """Circle sticker. dark+transparent → no plate, light text for dark surfaces."""
    if transparent:
        sticker = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    else:
        sticker = Image.new("RGBA", (size, size), WHITE)
        sticker.putalpha(circle_mask(size))

    # Edge ring: brand blue on light; soft light ring on dark transparent
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    stroke = max(4, size // 120)
    ring_color = (255, 255, 255, 200) if dark and transparent else BLUE_MID
    rd.ellipse(
        (stroke, stroke, size - stroke - 1, size - stroke - 1),
        outline=ring_color,
        width=stroke,
    )
    sticker.alpha_composite(ring)

    # Layout inspired by Yandex «Хорошее место» stack:
    # mark → light label → bold title → footer mark (QR)
    logo_size = int(size * 0.40)  # large logo, room for full title + QR
    logo = prep_logo(logo_size)
    logo_x = (size - logo_size) // 2
    logo_y = int(size * 0.07)
    sticker.alpha_composite(logo, (logo_x, logo_y))

    draw = ImageDraw.Draw(sticker)
    we_font = load_font(FONT_TEXT, int(size * 0.036), 500)
    brand_font = load_font(FONT_DISPLAY, int(size * 0.062), 800)
    url_font = load_font(FONT_TEXT, int(size * 0.024), 500)

    we = "МЫ В"
    brand = "КРУЖИМ"
    url = "kruzhim.ru"

    we_color = LIGHT if dark else INK
    url_color = SKY if dark else BLUE_DEEP

    we_bbox = draw.textbbox((0, 0), we, font=we_font)
    brand_bbox = draw.textbbox((0, 0), brand, font=brand_font)
    we_w = we_bbox[2] - we_bbox[0]
    brand_w = brand_bbox[2] - brand_bbox[0]
    brand_h = brand_bbox[3] - brand_bbox[1]

    text_top = logo_y + logo_size + int(size * 0.01)
    draw.text(((size - we_w) / 2, text_top), we, fill=we_color, font=we_font)

    brand_y = text_top + int(size * 0.04)
    draw.text(((size - brand_w) / 2, brand_y), brand, fill=ORANGE, font=brand_font)

    # QR below full title with clear gap (no overlap with letter bottoms)
    qr_inner = int(size * 0.16)
    qr = prep_qr(qr_inner)
    qr_x = (size - qr.size[0]) // 2
    qr_y = brand_y + brand_h + int(size * 0.055)
    sticker.alpha_composite(qr, (qr_x, qr_y))

    url_bbox = draw.textbbox((0, 0), url, font=url_font)
    url_w = url_bbox[2] - url_bbox[0]
    url_y = qr_y + qr.size[1] + int(size * 0.014)
    draw.text(((size - url_w) / 2, url_y), url, fill=url_color, font=url_font)

    if not shadow:
        return sticker

    stage_bg = (18, 24, 40, 255) if dark else (240, 245, 255, 255)
    stage = Image.new("RGBA", (size + 120, size + 120), stage_bg)
    # Checker hint for transparency on dark preview
    if transparent and dark:
        chk = ImageDraw.Draw(stage)
        cell = 28
        for yy in range(0, stage.size[1], cell):
            for xx in range(0, stage.size[0], cell):
                if (xx // cell + yy // cell) % 2 == 0:
                    chk.rectangle((xx, yy, xx + cell, yy + cell), fill=(28, 36, 56, 255))
    shadow_layer = Image.new("RGBA", stage.size, (0, 0, 0, 0))
    shadow_blob = Image.new("RGBA", (size, size), (0, 0, 0, 90))
    shadow_blob.putalpha(circle_mask(size).point(lambda p: int(p * 0.4) if p else 0))
    shadow_layer.paste(shadow_blob, (70, 78), shadow_blob)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(28))
    stage.alpha_composite(shadow_layer)
    stage.alpha_composite(sticker, (60, 50))
    return stage


def draw_door_preview(sticker: Image.Image) -> Image.Image:
    W, H = 900, 1400
    door = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(door)

    d.rounded_rectangle((40, 40, W - 40, H - 40), radius=28, fill=(223, 227, 232, 255))
    d.rounded_rectangle((58, 58, W - 58, H - 58), radius=18, fill=(122, 147, 168, 255))

    glass = Image.new("RGBA", (W - 140, H - 160), (158, 180, 200, 255))
    gdraw = ImageDraw.Draw(glass)
    for y in range(glass.height):
        t = y / max(glass.height - 1, 1)
        gdraw.line(
            [(0, y), (glass.width, y)],
            fill=(int(158 - 20 * t), int(180 - 30 * t), int(200 - 35 * t), 255),
        )
    door.paste(glass, (70, 80))

    highlight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(highlight).polygon(
        [(90, 90), (320, 90), (180, H - 100), (90, H - 140)],
        fill=(255, 255, 255, 38),
    )
    door.alpha_composite(highlight)

    sticker_px = 440
    s = sticker.resize((sticker_px, sticker_px), Image.Resampling.LANCZOS)
    sx = (W - sticker_px) // 2
    sy = (H - sticker_px) // 2 - 40

    sh = Image.new("RGBA", (sticker_px + 40, sticker_px + 40), (0, 0, 0, 0))
    blob = Image.new("RGBA", (sticker_px, sticker_px), (0, 0, 0, 90))
    blob.putalpha(circle_mask(sticker_px).point(lambda p: int(p * 0.4) if p else 0))
    sh.paste(blob, (12, 16), blob)
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    door.alpha_composite(sh, (sx - 12, sy - 8))
    door.alpha_composite(s, (sx, sy))

    stage = Image.new("RGBA", (W + 80, H + 80), (245, 246, 248, 255))
    stage.alpha_composite(door, (40, 40))
    return stage


def main() -> None:
    transparent = draw_sticker(SIZE, shadow=False)
    transparent.save(OUT_TRANSPARENT, "PNG")

    staged = draw_sticker(SIZE, shadow=True)
    staged.save(OUT_STICKER, "PNG")

    print_asset = draw_sticker(2362, shadow=False)
    print_asset.save(OUT_PRINT, "PNG")

    door = draw_door_preview(transparent)
    door.save(OUT_DOOR, "PNG")

    dark_print = draw_sticker(SIZE, shadow=False, dark=True, transparent=True)
    dark_print.save(OUT_DARK_PRINT, "PNG")
    draw_sticker(SIZE, shadow=True, dark=True, transparent=True).save(OUT_DARK, "PNG")

    print(f"Wrote {OUT_STICKER}")
    print(f"Wrote {OUT_TRANSPARENT}")
    print(f"Wrote {OUT_PRINT}")
    print(f"Wrote {OUT_DOOR}")
    print(f"Wrote {OUT_DARK}")
    print(f"Wrote {OUT_DARK_PRINT}")


if __name__ == "__main__":
    main()
