#!/usr/bin/env python3
"""Generate FarCar S400 / CarWebGuru theme assets (1280x720)."""

from __future__ import annotations

import math
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WALL = ROOT / "assets" / "wallpapers"
LOGOS = ROOT / "assets" / "logos"
CARS = ROOT / "assets" / "cars"
BOOT = ROOT / "assets" / "boot"
PREVIEWS = ROOT / "assets" / "previews"
ICONS = ROOT / "assets" / "icons"

W, H = 1280, 720

THEMES = {
    "pajero4": {
        "title": "Pajero 4",
        "accent": (201, 148, 54),
        "accent2": (90, 120, 70),
        "bg": (8, 10, 8),
        "fg": (230, 220, 190),
        "tag": "OFFROAD",
        "mark": "diamond",
    },
    "avengers": {
        "title": "Мстители",
        "accent": (196, 42, 48),
        "accent2": (40, 80, 180),
        "bg": (6, 8, 18),
        "fg": (220, 228, 240),
        "tag": "HEROES",
        "mark": "shield",
    },
    "venom": {
        "title": "Веном",
        "accent": (220, 230, 235),
        "accent2": (40, 180, 160),
        "bg": (4, 4, 6),
        "fg": (235, 240, 245),
        "tag": "SYMBIOTE",
        "mark": "tendril",
    },
    "gangsterland": {
        "title": "Ганстерленд",
        "accent": (212, 175, 55),
        "accent2": (150, 30, 40),
        "bg": (8, 6, 4),
        "fg": (240, 230, 200),
        "tag": "NOIR",
        "mark": "deco",
    },
    "black-dragon": {
        "title": "Чёрный Дракон",
        "accent": (190, 30, 40),
        "accent2": (212, 175, 55),
        "bg": (6, 4, 4),
        "fg": (245, 230, 210),
        "tag": "DRAGON",
        "mark": "dragon",
    },
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    paths = [
        "/usr/share/fonts/truetype/noto/NotoSansDisplay-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDisplay-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def ensure_dirs() -> None:
    for d in (LOGOS, CARS, BOOT, PREVIEWS, ICONS):
        d.mkdir(parents=True, exist_ok=True)
        for key in THEMES:
            (d / key).mkdir(parents=True, exist_ok=True)


def draw_mark(draw: ImageDraw.ImageDraw, mark: str, cx: int, cy: int, r: int, color: tuple[int, int, int], width: int = 6) -> None:
    if mark == "diamond":
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        draw.polygon(pts, outline=color)
        draw.line(pts + [pts[0]], fill=color, width=width)
        draw.polygon([(cx, cy - r // 2), (cx + r // 2, cy), (cx, cy + r // 2), (cx - r // 2, cy)], outline=color)
    elif mark == "shield":
        pts = [
            (cx, cy - r),
            (cx + r * 0.85, cy - r * 0.55),
            (cx + r * 0.75, cy + r * 0.2),
            (cx, cy + r),
            (cx - r * 0.75, cy + r * 0.2),
            (cx - r * 0.85, cy - r * 0.55),
        ]
        draw.polygon([(int(x), int(y)) for x, y in pts], outline=color)
        draw.ellipse((cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3), outline=color, width=width)
    elif mark == "tendril":
        for i in range(6):
            a = i * math.pi / 3
            x2 = cx + int(math.cos(a) * r)
            y2 = cy + int(math.sin(a) * r)
            draw.line((cx, cy, x2, y2), fill=color, width=width)
            draw.ellipse((x2 - 10, y2 - 10, x2 + 10, y2 + 10), fill=color)
        draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=color)
    elif mark == "deco":
        draw.rectangle((cx - r, cy - r // 3, cx + r, cy + r // 3), outline=color, width=width)
        draw.line((cx - r, cy, cx + r, cy), fill=color, width=2)
        draw.polygon([(cx, cy - r), (cx + 12, cy - r // 3), (cx - 12, cy - r // 3)], fill=color)
        draw.polygon([(cx, cy + r), (cx + 12, cy + r // 3), (cx - 12, cy + r // 3)], fill=color)
    elif mark == "dragon":
        # stylized spiral / eye
        for k in range(3):
            rr = r - k * 18
            draw.arc((cx - rr, cy - rr, cx + rr, cy + rr), 40, 300, fill=color, width=width)
        draw.ellipse((cx + r // 4 - 8, cy - 8, cx + r // 4 + 8, cy + 8), fill=color)


def make_logo(key: str, cfg: dict) -> None:
    size = 350
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # dark disc
    d.ellipse((8, 8, size - 8, size - 8), fill=(*cfg["bg"], 230))
    d.ellipse((8, 8, size - 8, size - 8), outline=(*cfg["accent"], 255), width=5)
    draw_mark(d, cfg["mark"], size // 2, size // 2 - 10, 90, cfg["accent"], 7)
    f = font(28, bold=True)
    text = cfg["title"]
    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    d.text(((size - tw) / 2, size - 58), text, font=f, fill=(*cfg["fg"], 255))
    out = LOGOS / key / "logo.png"
    img.save(out)
    # also 250 variant
    img.resize((250, 250), Image.Resampling.LANCZOS).save(LOGOS / key / "logo_250.png")


def make_car(key: str, cfg: dict) -> None:
    """Car PNGs for CWG. Keep hand-authored source if present."""
    stop = CARS / key / "car_stop.png"
    move = CARS / key / "car_move.png"
    if stop.exists() and move.exists() and stop.stat().st_size > 20_000:
        # already have detailed assets
        stop_img = Image.open(stop).convert("RGBA")
        if stop_img.size != (500, 250):
            canvas = Image.new("RGBA", (500, 250), (0, 0, 0, 0))
            stop_img.thumbnail((480, 230), Image.Resampling.LANCZOS)
            canvas.paste(stop_img, ((500 - stop_img.width) // 2, 250 - stop_img.height - 8), stop_img)
            canvas.save(stop)
            canvas.resize((300, 150), Image.Resampling.LANCZOS).save(CARS / key / "car_stop_sm.png")
        move_img = Image.open(move).convert("RGBA")
        if move_img.size != (500, 250):
            canvas = Image.new("RGBA", (500, 250), (0, 0, 0, 0))
            move_img.thumbnail((480, 230), Image.Resampling.LANCZOS)
            canvas.paste(move_img, ((500 - move_img.width) // 2, 250 - move_img.height - 8), move_img)
            canvas.save(move)
            canvas.resize((300, 150), Image.Resampling.LANCZOS).save(CARS / key / "car_move_sm.png")
        return

    for moving, name in ((False, "car_stop.png"), (True, "car_move.png")):
        img = Image.new("RGBA", (500, 250), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        accent = cfg["accent"]
        body = (28, 28, 30, 240)
        # body
        d.rounded_rectangle((60, 90, 430, 170), radius=18, fill=body)
        d.polygon([(120, 90), (180, 45), (320, 45), (380, 90)], fill=body)
        # windows
        d.polygon([(185, 55), (250, 55), (250, 88), (160, 88)], fill=(40, 60, 80, 180))
        d.polygon([(255, 55), (315, 55), (360, 88), (255, 88)], fill=(40, 60, 80, 160))
        # wheels
        for wx in (130, 360):
            d.ellipse((wx, 145, wx + 55, 200), fill=(10, 10, 10, 255))
            d.ellipse((wx + 12, 157, wx + 43, 188), fill=(*accent, 180 if moving else 80))
        # lights
        if moving:
            d.ellipse((415, 115, 440, 140), fill=(*accent, 255))
            d.ellipse((50, 120, 72, 145), fill=(200, 40, 40, 220))
            # light beams
            for i in range(3):
                beam = Image.new("RGBA", img.size, (0, 0, 0, 0))
                bd = ImageDraw.Draw(beam)
                bd.polygon(
                    [(430, 125), (500, 90 + i * 25), (500, 120 + i * 25)],
                    fill=(*accent, 35),
                )
                img = Image.alpha_composite(img, beam)
        else:
            d.ellipse((415, 115, 440, 140), fill=(*accent, 90))
            d.ellipse((50, 120, 72, 145), fill=(120, 30, 30, 160))
        img.save(CARS / key / name)
        # also 300x150
        img.resize((300, 150), Image.Resampling.LANCZOS).save(CARS / key / name.replace(".png", "_sm.png"))


def make_boot(key: str, cfg: dict, wallpaper: Path) -> None:
    # logo.bmp 24-bit
    base = Image.open(wallpaper).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 140))
    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(base)
    draw_mark(d, cfg["mark"], W // 2, H // 2 - 40, 110, cfg["accent"], 8)
    f = font(54, bold=True)
    text = cfg["title"]
    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) / 2, H // 2 + 90), text, font=f, fill=cfg["fg"])
    tf = font(22)
    tag = f"FARCAR S400  ·  {cfg['tag']}"
    bbox = d.textbbox((0, 0), tag, font=tf)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) / 2, H // 2 + 155), tag, font=tf, fill=cfg["accent"])
    bmp_path = BOOT / key / "logo.bmp"
    base.save(bmp_path, format="BMP")

    # bootanimation.zip — short fade sequence
    anim_dir = BOOT / key / "_frames"
    anim_dir.mkdir(exist_ok=True)
    part = anim_dir / "part0"
    part.mkdir(exist_ok=True)
    frames = []
    for i in range(24):
        t = i / 23
        frame = Image.new("RGB", (W, H), cfg["bg"])
        fd = ImageDraw.Draw(frame)
        alpha = min(1.0, t * 1.4)
        # fade mark
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        col = tuple(int(c * alpha) for c in cfg["accent"]) + (int(255 * alpha),)
        # approximate with solid
        draw_mark(ld, cfg["mark"], W // 2, H // 2 - 20, int(80 + 40 * alpha), cfg["accent"], 7)
        frame = Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")
        fd = ImageDraw.Draw(frame)
        if t > 0.35:
            a2 = min(1.0, (t - 0.35) / 0.5)
            fnt = font(48, bold=True)
            bbox = fd.textbbox((0, 0), text, font=fnt)
            tw = bbox[2] - bbox[0]
            fg = tuple(int(c * a2) for c in cfg["fg"])
            fd.text(((W - tw) / 2, H // 2 + 100), text, font=fnt, fill=fg)
        # progress bar
        if t > 0.2:
            bw = int((W * 0.4) * min(1.0, (t - 0.2) / 0.8))
            fd.rectangle((W // 2 - 200, H - 80, W // 2 + 200, H - 68), outline=cfg["accent"])
            fd.rectangle((W // 2 - 200, H - 80, W // 2 - 200 + bw, H - 68), fill=cfg["accent"])
        fp = part / f"{i:04d}.jpg"
        frame.save(fp, quality=90)
        frames.append(fp)

    desc = f"""{W} {H} 24
p 1 0 part0
"""
    zip_path = BOOT / key / "bootanimation.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("desc.txt", desc)
        for fp in frames:
            zf.write(fp, f"part0/{fp.name}")

    # cleanup frames to keep repo smaller
    for fp in frames:
        fp.unlink()
    part.rmdir()
    anim_dir.rmdir()


def make_icons(key: str, cfg: dict) -> None:
    names = {
        "nav": "НАВИ",
        "radio": "РАДИО",
        "music": "МУЗЫКА",
        "bt": "BT",
        "apps": "ПРОГИ",
        "settings": "НАСТР",
        "cam": "КАМЕРА",
        "phone": "ЗВОНОК",
    }
    for name, label in names.items():
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((4, 4, 124, 124), radius=22, fill=(*cfg["bg"], 220), outline=(*cfg["accent"], 255), width=3)
        f = font(18, bold=True)
        bbox = d.textbbox((0, 0), label, font=f)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((128 - tw) / 2, (128 - th) / 2 - 2), label, font=f, fill=(*cfg["fg"], 255))
        img.save(ICONS / key / f"{name}.png")


def make_preview(key: str, cfg: dict, wallpaper: Path) -> None:
    """Dashboard DX-like layout preview for gallery."""
    bg = Image.open(wallpaper).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 110))
    img = Image.alpha_composite(bg, shade)
    d = ImageDraw.Draw(img)

    # left gauge panel
    d.rounded_rectangle((30, 80, 340, 560), radius=24, fill=(10, 10, 12, 200), outline=(*cfg["accent"], 180), width=2)
    # speed ring
    cx, cy, r = 185, 280, 110
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*cfg["accent"], 255), width=8)
    d.ellipse((cx - r + 20, cy - r + 20, cx + r - 20, cy + r - 20), outline=(*cfg["accent2"], 160), width=3)
    sf = font(64, bold=True)
    d.text((cx - 40, cy - 40), "86", font=sf, fill=cfg["fg"])
    d.text((cx - 28, cy + 30), "км/ч", font=font(20), fill=cfg["accent"])

    # right music panel
    d.rounded_rectangle((940, 80, 1250, 560), radius=24, fill=(10, 10, 12, 200), outline=(*cfg["accent"], 180), width=2)
    d.rounded_rectangle((1000, 140, 1190, 330), radius=16, fill=(*cfg["accent"], 40), outline=(*cfg["accent"], 120), width=2)
    d.text((1020, 360), "Now Playing", font=font(18), fill=cfg["accent"])
    d.text((1020, 390), "Night Drive", font=font(28, bold=True), fill=cfg["fg"])
    d.text((1020, 430), "Theme Pack", font=font(18), fill=(180, 180, 180))
    # transport
    for i, x in enumerate((1020, 1090, 1160)):
        d.ellipse((x, 480, x + 50, 530), outline=(*cfg["accent"], 220), width=2)

    # center car road
    d.rounded_rectangle((380, 160, 900, 480), radius=20, fill=(0, 0, 0, 90))
    # road lines
    for y in range(220, 460, 40):
        d.rectangle((620, y, 660, y + 18), fill=(*cfg["accent"], 80))

    # top bar
    d.text((40, 24), "14:32", font=font(36, bold=True), fill=cfg["fg"])
    d.text((160, 36), "ПН  ·  16 НОЯ", font=font(18), fill=cfg["accent"])
    d.text((W // 2 - 80, 28), cfg["title"], font=font(28, bold=True), fill=cfg["fg"])

    # bottom apps
    labels = ["НАВИ", "РАДИО", "МУЗЫКА", "BT", "ПРОГИ", "НАСТР"]
    for i, lab in enumerate(labels):
        x = 80 + i * 190
        d.rounded_rectangle((x, 600, x + 150, 680), radius=16, fill=(12, 12, 14, 210), outline=(*cfg["accent"], 160), width=2)
        bbox = d.textbbox((0, 0), lab, font=font(18, bold=True))
        tw = bbox[2] - bbox[0]
        d.text((x + (150 - tw) / 2, 630), lab, font=font(18, bold=True), fill=cfg["fg"])

    img.convert("RGB").save(PREVIEWS / key / "dashboard.jpg", quality=92)


def package_cwg_folder(key: str) -> None:
    """Zip folder ready to copy into /CarWebGuru/cfg and wallpapers."""
    import shutil

    pack = ROOT / "packs" / key
    if pack.exists():
        shutil.rmtree(pack)
    pack.mkdir(parents=True, exist_ok=True)
    cfg = pack / "CarWebGuru" / "cfg"
    cfg.mkdir(parents=True, exist_ok=True)
    # logos + cars
    for src in (LOGOS / key / "logo.png", CARS / key / "car_move.png", CARS / key / "car_stop.png"):
        if src.exists():
            dest_name = src.name if "car_" in src.name else f"logo_{key}.png"
            if src.name == "logo.png":
                dest_name = f"{key}_logo.png"
            Image.open(src).save(cfg / dest_name)
    # wallpaper
    wall = WALL / f"bg-{key}.jpg"
    if wall.exists():
        Image.open(wall).convert("RGB").resize((W, H)).save(pack / "wallpaper.jpg", quality=95)
    # boot
    boot_dst = pack / "boot"
    boot_dst.mkdir(exist_ok=True)
    for name in ("logo.bmp", "bootanimation.zip"):
        src = BOOT / key / name
        if src.exists():
            (boot_dst / name).write_bytes(src.read_bytes())
    # zip pack
    zip_path = ROOT / "packs" / f"{key}-farcar-s400.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in pack.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(pack).as_posix())
    shutil.rmtree(pack)


def main() -> None:
    ensure_dirs()
    for key, cfg in THEMES.items():
        wall = WALL / f"bg-{key}.jpg"
        if not wall.exists():
            print(f"missing wallpaper {wall}")
            continue
        print(f"building {key}...")
        make_logo(key, cfg)
        make_car(key, cfg)
        make_boot(key, cfg, wall)
        make_icons(key, cfg)
        make_preview(key, cfg, wall)
        package_cwg_folder(key)
    print("done")


if __name__ == "__main__":
    main()
