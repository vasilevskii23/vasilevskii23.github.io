#!/usr/bin/env python3
"""Generate car sticker mockups from the latest КРУЖИМ door sticker design."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from generate_sticker import (
    BLUE_DEEP,
    BLUE_MID,
    FONT_DISPLAY,
    FONT_TEXT,
    INK,
    ORANGE,
    ROOT,
    WHITE,
    circle_mask,
    draw_sticker,
    load_font,
    prep_logo,
    prep_qr,
)

OUT_CIRCLE = ROOT / "car_sticker.png"
OUT_CIRCLE_PRINT = ROOT / "car_sticker_print.png"
OUT_HORIZONTAL = ROOT / "car_sticker_horizontal.png"
OUT_HORIZONTAL_PRINT = ROOT / "car_sticker_horizontal_print.png"
OUT_PREVIEW = ROOT / "car_preview.png"


def with_stage(sticker: Image.Image, pad: int = 80, bg=(240, 245, 255, 255)) -> Image.Image:
    w, h = sticker.size
    stage = Image.new("RGBA", (w + pad * 2, h + pad * 2), bg)
    shadow = Image.new("RGBA", stage.size, (0, 0, 0, 0))
    # Soft shadow under sticker bounds
    blob = Image.new("RGBA", (w, h), (13, 31, 92, 0))
    alpha = sticker.split()[-1].point(lambda p: int(p * 0.35) if p else 0)
    blob.putalpha(alpha)
    shadow.paste(blob, (pad + 8, pad + 14), blob)
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    stage.alpha_composite(shadow)
    stage.alpha_composite(sticker, (pad, pad))
    return stage


def draw_horizontal_car_sticker(width: int = 2400, height: int = 900) -> Image.Image:
    """Bumper / rear-window friendly layout: logo | copy | QR."""
    sticker = Image.new("RGBA", (width, height), WHITE)
    radius = height // 2  # stadium / pill shape — common car-window cut
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    sticker.putalpha(mask)

    # Brand outline
    outline = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(outline)
    stroke = max(4, height // 45)
    od.rounded_rectangle(
        (stroke, stroke, width - stroke - 1, height - stroke - 1),
        radius=radius - stroke,
        outline=BLUE_MID,
        width=stroke,
    )
    sticker.alpha_composite(outline)

    # Left: large logo
    logo_size = int(height * 0.72)
    logo = prep_logo(logo_size)
    logo_x = int(width * 0.06)
    logo_y = (height - logo_size) // 2
    sticker.alpha_composite(logo, (logo_x, logo_y))

    # Center: МЫ В / КРУЖИМ / url
    draw = ImageDraw.Draw(sticker)
    we_font = load_font(FONT_TEXT, int(height * 0.12), 500)
    brand_font = load_font(FONT_DISPLAY, int(height * 0.22), 800)
    url_font = load_font(FONT_TEXT, int(height * 0.08), 500)

    we, brand, url = "МЫ В", "КРУЖИМ", "kruzhim.ru"
    text_left = logo_x + logo_size + int(width * 0.04)

    we_bbox = draw.textbbox((0, 0), we, font=we_font)
    brand_bbox = draw.textbbox((0, 0), brand, font=brand_font)
    url_bbox = draw.textbbox((0, 0), url, font=url_font)
    we_h = we_bbox[3] - we_bbox[1]
    brand_h = brand_bbox[3] - brand_bbox[1]
    url_h = url_bbox[3] - url_bbox[1]
    gap1, gap2 = int(height * 0.04), int(height * 0.05)
    block_h = we_h + gap1 + brand_h + gap2 + url_h
    y = (height - block_h) // 2 - int(height * 0.02)

    draw.text((text_left, y), we, fill=INK, font=we_font)
    y2 = y + we_h + gap1
    draw.text((text_left, y2), brand, fill=ORANGE, font=brand_font)
    y3 = y2 + brand_h + gap2
    draw.text((text_left, y3), url, fill=BLUE_DEEP, font=url_font)

    # Right: QR
    qr_inner = int(height * 0.42)
    qr = prep_qr(qr_inner)
    qr_x = width - qr.size[0] - int(width * 0.07)
    qr_y = (height - qr.size[1]) // 2
    sticker.alpha_composite(qr, (qr_x, qr_y))

    return sticker


def draw_car_preview(circle: Image.Image, horizontal: Image.Image) -> Image.Image:
    """Simple side/rear car mockup with both sticker placements."""
    W, H = 1600, 1000
    stage = Image.new("RGBA", (W, H), (230, 236, 245, 255))

    # Asphalt strip
    d = ImageDraw.Draw(stage)
    d.rectangle((0, int(H * 0.72), W, H), fill=(55, 62, 72, 255))
    d.rectangle((0, int(H * 0.72), W, int(H * 0.74)), fill=(90, 96, 104, 255))

    # Car body silhouette (compact hatchback-ish)
    car = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(car)
    body = (220, 38, 48, 255)
    dark = (140, 22, 30, 255)
    glass = (120, 160, 190, 210)

    # Main body
    cd.rounded_rectangle((180, 420, 1420, 720), radius=48, fill=body)
    # Cabin
    cd.polygon(
        [(380, 420), (520, 260), (980, 260), (1180, 420)],
        fill=body,
    )
    # Windows
    cd.polygon(
        [(420, 410), (535, 280), (960, 280), (1120, 410)],
        fill=glass,
    )
    # Window divider
    cd.line([(760, 280), (760, 410)], fill=(90, 120, 145, 255), width=6)
    # Wheels
    for cx in (420, 1180):
        cd.ellipse((cx - 70, 660, cx + 70, 800), fill=(30, 30, 34, 255))
        cd.ellipse((cx - 38, 692, cx + 38, 768), fill=(90, 90, 98, 255))
    # Headlight / taillight accents
    cd.rounded_rectangle((190, 500, 250, 560), radius=12, fill=(255, 220, 120, 230))
    cd.rounded_rectangle((1350, 500, 1410, 560), radius=12, fill=ORANGE)
    # Shadow under car
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((260, 760, 1340, 820), fill=(0, 0, 0, 60))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    stage.alpha_composite(sh)
    stage.alpha_composite(car)

    # Circle sticker on rear side window (right window)
    csize = 170
    c = circle.resize((csize, csize), Image.Resampling.LANCZOS)
    stage.alpha_composite(c, (880, 300))

    # Horizontal sticker on rear bumper area
    h_w, h_h = 520, 195
    h = horizontal.resize((h_w, h_h), Image.Resampling.LANCZOS)
    stage.alpha_composite(h, (W - h_w - 90, 545))

    # Labels
    label_font = load_font(FONT_TEXT, 28, 600)
    title_font = load_font(FONT_DISPLAY, 36, 700)
    d2 = ImageDraw.Draw(stage)
    d2.text((60, 48), "НАКЛЕЙКА НА МАШИНУ", fill=INK, font=title_font)
    d2.text((60, 100), "круг на стекло  ·  горизонталь на кузов", fill=BLUE_DEEP, font=label_font)

    return stage


def main() -> None:
    # Circular — same latest door layout, print for auto glass (~Ø18 cm @ 300dpi ≈ 2126 px)
    circle_print = draw_sticker(2126, shadow=False)
    circle_print.save(OUT_CIRCLE_PRINT, "PNG")
    with_stage(circle_print).save(OUT_CIRCLE, "PNG")

    # Horizontal bumper / rear glass
    horizontal_print = draw_horizontal_car_sticker(2400, 900)
    horizontal_print.save(OUT_HORIZONTAL_PRINT, "PNG")
    with_stage(horizontal_print, pad=70).save(OUT_HORIZONTAL, "PNG")

    preview = draw_car_preview(circle_print, horizontal_print)
    preview.save(OUT_PREVIEW, "PNG")

    print(f"Wrote {OUT_CIRCLE}")
    print(f"Wrote {OUT_CIRCLE_PRINT}")
    print(f"Wrote {OUT_HORIZONTAL}")
    print(f"Wrote {OUT_HORIZONTAL_PRINT}")
    print(f"Wrote {OUT_PREVIEW}")


if __name__ == "__main__":
    main()
