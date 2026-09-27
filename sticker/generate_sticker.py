#!/usr/bin/env python3
"""Generate circular door sticker mockups for КРУЖИМ."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "logo.jpg"
OUT_STICKER = ROOT / "sticker.png"
OUT_TRANSPARENT = ROOT / "sticker_transparent.png"
OUT_DOOR = ROOT / "door_preview.png"
OUT_PRINT = ROOT / "sticker_print_300dpi.png"

SIZE = 2000  # px
MARGIN = 0.14
LOGO_RATIO = 0.36
FONT_REG = "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"


def circle_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def prep_logo(target: int) -> Image.Image:
    logo = Image.open(LOGO).convert("RGBA")
    # Crop to content circle: logo is already circular on light bg
    w, h = logo.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    logo = logo.crop((left, top, left + side, top + side))
    logo = logo.resize((target, target), Image.Resampling.LANCZOS)

    # Soft circular clip in case of square corners
    mask = circle_mask(target)
    out = Image.new("RGBA", (target, target), (0, 0, 0, 0))
    out.paste(logo, (0, 0), mask)
    return out


def draw_sticker(size: int = SIZE, shadow: bool = True) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sticker = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    sticker.putalpha(circle_mask(size))

    logo_size = int(size * LOGO_RATIO)
    logo = prep_logo(logo_size)

    # Vertical composition inspired by Yandex award stickers:
    # logo upper half, text lower — generous white space.
    logo_x = (size - logo_size) // 2
    logo_y = int(size * 0.18)
    sticker.alpha_composite(logo, (logo_x, logo_y))

    draw = ImageDraw.Draw(sticker)
    we_font = ImageFont.truetype(FONT_REG, int(size * 0.048))
    brand_font = ImageFont.truetype(FONT_BOLD, int(size * 0.088))

    we = "МЫ В"
    brand = "КРУЖИМ"

    we_bbox = draw.textbbox((0, 0), we, font=we_font)
    brand_bbox = draw.textbbox((0, 0), brand, font=brand_font)
    we_w = we_bbox[2] - we_bbox[0]
    brand_w = brand_bbox[2] - brand_bbox[0]

    text_top = logo_y + logo_size + int(size * 0.055)
    draw.text(((size - we_w) / 2, text_top), we, fill=(26, 26, 26, 255), font=we_font)
    brand_y = text_top + int(size * 0.055)
    draw.text(((size - brand_w) / 2, brand_y), brand, fill=(26, 26, 26, 255), font=brand_font)

    if not shadow:
        return sticker

    # Soft physical-sticker shadow on neutral stage
    stage = Image.new("RGBA", (size + 120, size + 120), (232, 234, 237, 255))
    shadow_layer = Image.new("RGBA", stage.size, (0, 0, 0, 0))
    shadow_mask = circle_mask(size)
    shadow_blob = Image.new("RGBA", (size, size), (0, 0, 0, 70))
    shadow_blob.putalpha(shadow_mask.point(lambda p: int(p * 0.35) if p else 0))
    shadow_layer.paste(shadow_blob, (70, 78), shadow_blob)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(28))
    stage.alpha_composite(shadow_layer)
    stage.alpha_composite(sticker, (60, 50))
    return stage


def draw_door_preview(sticker: Image.Image) -> Image.Image:
    W, H = 900, 1400
    door = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(door)

    # Frame
    d.rounded_rectangle((40, 40, W - 40, H - 40), radius=28, fill=(223, 227, 232, 255))
    d.rounded_rectangle((58, 58, W - 58, H - 58), radius=18, fill=(122, 147, 168, 255))

    # Glass gradient feel
    glass = Image.new("RGBA", (W - 140, H - 160), (158, 180, 200, 255))
    gdraw = ImageDraw.Draw(glass)
    for y in range(glass.height):
        t = y / max(glass.height - 1, 1)
        r = int(158 - 20 * t)
        g = int(180 - 30 * t)
        b = int(200 - 35 * t)
        gdraw.line([(0, y), (glass.width, y)], fill=(r, g, b, 255))
    door.paste(glass, (70, 80))

    # Highlight
    highlight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    hd.polygon([(90, 90), (320, 90), (180, H - 100), (90, H - 140)], fill=(255, 255, 255, 38))
    door.alpha_composite(highlight)

    # Sticker (transparent version scaled)
    sticker_px = 420
    s = sticker.resize((sticker_px, sticker_px), Image.Resampling.LANCZOS)
    sx = (W - sticker_px) // 2
    sy = (H - sticker_px) // 2 - 40

    # sticker shadow on glass
    sh = Image.new("RGBA", (sticker_px + 40, sticker_px + 40), (0, 0, 0, 0))
    sm = circle_mask(sticker_px)
    blob = Image.new("RGBA", (sticker_px, sticker_px), (0, 0, 0, 90))
    blob.putalpha(sm.point(lambda p: int(p * 0.4) if p else 0))
    sh.paste(blob, (12, 16), blob)
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    door.alpha_composite(sh, (sx - 12, sy - 8))
    door.alpha_composite(s, (sx, sy))

    # Outer stage
    stage = Image.new("RGBA", (W + 80, H + 80), (245, 246, 248, 255))
    stage.alpha_composite(door, (40, 40))
    return stage


def main() -> None:
    transparent = draw_sticker(SIZE, shadow=False)
    transparent.save(OUT_TRANSPARENT, "PNG")

    staged = draw_sticker(SIZE, shadow=True)
    staged.save(OUT_STICKER, "PNG")

    # 300dpi ~ 10cm diameter print asset (1181px); keep high-res transparent
    print_size = 2362  # ~20cm @ 300dpi, good for door sticker
    print_asset = draw_sticker(print_size, shadow=False)
    print_asset.save(OUT_PRINT, "PNG")

    door = draw_door_preview(transparent)
    door.save(OUT_DOOR, "PNG")

    print(f"Wrote {OUT_STICKER}")
    print(f"Wrote {OUT_TRANSPARENT}")
    print(f"Wrote {OUT_PRINT}")
    print(f"Wrote {OUT_DOOR}")


if __name__ == "__main__":
    main()
