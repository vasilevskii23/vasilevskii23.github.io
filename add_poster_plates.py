#!/usr/bin/env python3
"""Add date/limited-seats plates to the «Поговори с ней» poster."""
from PIL import Image, ImageDraw, ImageFont
import os

SRC = os.path.join(os.path.dirname(__file__), "pogovori-s-ney-original.jpg")
OUT = os.path.join(os.path.dirname(__file__), "pogovori-s-ney-poster.jpg")

YELLOW = (255, 202, 0, 255)
WHITE = (255, 255, 255, 255)
BLACK = (12, 12, 12, 255)

def make_plate(text, font, bg, fg=BLACK, pad_x=20, pad_y=10, angle=-9, outline=None, outline_w=3):
    tmp = Image.new("RGBA", (4, 4))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pw, ph = tw + pad_x * 2, th + pad_y * 2
    plate = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    if outline is not None:
        pd.rectangle([0, 0, pw - 1, ph - 1], fill=outline)
        pd.rectangle([outline_w, outline_w, pw - 1 - outline_w, ph - 1 - outline_w], fill=bg)
    else:
        pd.rectangle([0, 0, pw - 1, ph - 1], fill=bg)
    pd.text((pad_x - bbox[0], pad_y - bbox[1]), text, font=font, fill=fg)
    return plate.rotate(angle, expand=True, resample=Image.BICUBIC)

def paste_at(base, overlay, left, top):
    base.alpha_composite(overlay, (int(left), int(top)))

def main():
    img = Image.open(SRC).convert("RGBA")
    font_dates = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 34)
    # 2x previous size (22 -> 44)
    font_lim = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 44)

    dates = make_plate("12 декабря, 23 декабря", font_dates, YELLOW, pad_x=18, pad_y=9, angle=-8)
    limited = make_plate("количество мест ограничено", font_lim, WHITE, pad_x=26, pad_y=14, angle=6)

    paste_at(img, dates, 24, 148)
    # Shift left a bit so the larger plate still fits on the red field
    paste_at(img, limited, 40, 1125)

    img.convert("RGB").save(OUT, quality=95, optimize=True)
    print("Wrote", OUT)

if __name__ == "__main__":
    main()
