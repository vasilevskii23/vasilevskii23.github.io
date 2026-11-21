#!/usr/bin/env python3
"""Build accurate cinematic /maps poster for Петербургский Мистериум route."""
from __future__ import annotations

import io
import json
import math
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

OUT_DIR = Path("/workspace/maps")
ART_DIR = Path("/opt/cursor/artifacts")

# Verified coordinates
ORIGIN = (59.94285, 30.34520)  # southern Моховая ул.
DEST = (59.94349, 30.30107)  # Биржевой проезд, 2
PALACE_BRIDGE = (59.94118, 30.30810)
ISAAC = (59.93415, 30.30610)
PPF = (59.95020, 30.31650)
Z = 14
TILE = 256
W_OUT, H_OUT = 1080, 1440


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "maps-agent/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_route(waypoints: list[tuple[float, float]]):
    # waypoints as (lat, lon)
    path = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{path}?overview=full&geometries=geojson"
    )
    data = fetch_json(url)
    if data.get("code") != "Ok":
        raise RuntimeError(data)
    return data["routes"][0]


def latlon_to_pixel(lat: float, lon: float, z: int):
    n = 2**z
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return x, y


def fetch_tile(tx: int, ty: int, z: int) -> Image.Image:
    # Prefer ArcGIS dark gray; fallback OSM
    urls = [
        f"https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{ty}/{tx}",
        f"https://tile.openstreetmap.org/{z}/{tx}/{ty}.png",
    ]
    last = None
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "maps-agent/1.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                im = Image.open(io.BytesIO(r.read())).convert("RGB")
            if im.size[0] != TILE:
                im = im.resize((TILE, TILE), Image.Resampling.LANCZOS)
            return im
        except Exception as e:  # noqa: BLE001
            last = e
    print("tile fail", tx, ty, last)
    return Image.new("RGB", (TILE, TILE), (10, 12, 18))


def cinematic_grade(im: Image.Image) -> Image.Image:
    """Dark teal-gold grade; obliterate base-map bilingual labels."""
    # Downscale/upscale + blur removes tile typography while keeping water/land
    small = im.resize((im.width // 3, im.height // 3), Image.Resampling.BILINEAR)
    soft = small.resize(im.size, Image.Resampling.BILINEAR)
    soft = soft.filter(ImageFilter.GaussianBlur(radius=2.4))
    soft = ImageEnhance.Contrast(soft).enhance(1.4)
    soft = ImageEnhance.Brightness(soft).enhance(0.68)
    soft = ImageEnhance.Color(soft).enhance(0.55)
    tint = Image.new("RGB", soft.size, (5, 14, 24))
    soft = Image.blend(soft, tint, 0.34)
    gray = soft.convert("L")
    gold = ImageOps.colorize(gray, black="#05070c", white="#c9a24b")
    soft = Image.blend(soft, gold, 0.2)
    return soft


def simplify_xy(xy: list[tuple[float, float]], step: int = 2):
    if len(xy) < 3:
        return xy
    out = xy[::step]
    if out[-1] != xy[-1]:
        out.append(xy[-1])
    return out


def draw_glow_line(draw: ImageDraw.ImageDraw, xy, rgb, width: int):
    xy = simplify_xy(xy, 2)
    for w, a in ((width + 18, 28), (width + 10, 55), (width + 4, 120), (width, 255)):
        draw.line(xy, fill=rgb + (a,), width=w, joint="curve")


def star_poly(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def load_font(path: str, size: int):
    return ImageFont.truetype(path, size)


def main():
    main_route = fetch_route([ORIGIN, DEST])
    # Purple alternate via Садовая → Невский (~+2 мин), as on the screenshot
    via_pts = [
        (59.9350, 30.3300),  # Садовая / Невский
        (59.9345, 30.3150),  # Невский к Адмиралтейству
    ]
    try:
        alt_route = fetch_route([ORIGIN, *via_pts, DEST])
    except Exception:
        alt_route = None

    print(
        f"main {main_route['distance']/1000:.2f} km / {main_route['duration']/60:.1f} min"
    )
    if alt_route:
        print(
            f"alt  {alt_route['distance']/1000:.2f} km / {alt_route['duration']/60:.1f} min"
        )

    main_coords = main_route["geometry"]["coordinates"]
    alt_coords = alt_route["geometry"]["coordinates"] if alt_route else None

    lats = [c[1] for c in main_coords] + [ORIGIN[0], DEST[0], 59.9525, 59.9290]
    lons = [c[0] for c in main_coords] + [ORIGIN[1], DEST[1], 30.2820, 30.3550]
    if alt_coords:
        lats += [c[1] for c in alt_coords]
        lons += [c[0] for c in alt_coords]

    min_lat, max_lat = min(lats) - 0.0025, max(lats) + 0.0025
    min_lon, max_lon = min(lons) - 0.004, max(lons) + 0.004

    x0, y1 = latlon_to_pixel(min_lat, min_lon, Z)
    x1, y0 = latlon_to_pixel(max_lat, max_lon, Z)
    tx0, tx1 = int(math.floor(x0)), int(math.floor(x1))
    ty0, ty1 = int(math.floor(y0)), int(math.floor(y1))

    W = (tx1 - tx0 + 1) * TILE
    H = (ty1 - ty0 + 1) * TILE
    print(f"tiles x{tx0}-{tx1} y{ty0}-{ty1} ({(tx1-tx0+1)*(ty1-ty0+1)} tiles)")

    base = Image.new("RGB", (W, H))
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            tile = fetch_tile(tx, ty, Z)
            base.paste(tile, ((tx - tx0) * TILE, (ty - ty0) * TILE))

    base = cinematic_grade(base)

    def to_xy(lat, lon):
        x, y = latlon_to_pixel(lat, lon, Z)
        return (x - tx0) * TILE, (y - ty0) * TILE

    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    if alt_coords:
        draw_glow_line(
            d, [to_xy(lat, lon) for lon, lat in alt_coords], (155, 109, 255), 4
        )
    draw_glow_line(d, [to_xy(lat, lon) for lon, lat in main_coords], (47, 224, 106), 6)

    ox, oy = to_xy(*ORIGIN)
    dx, dy = to_xy(*DEST)

    # Start: gold star
    d.ellipse([ox - 28, oy - 28, ox + 28, oy + 28], fill=(255, 210, 58, 40))
    d.polygon(star_poly(ox, oy, 18, 8), fill=(255, 214, 70, 255))

    # Dest: green building pin
    d.ellipse([dx - 26, dy - 26, dx + 26, dy + 26], fill=(47, 224, 106, 40))
    d.rounded_rectangle(
        [dx - 15, dy - 18, dx + 15, dy + 8],
        radius=3,
        fill=(14, 36, 24, 255),
        outline=(47, 224, 106, 255),
        width=2,
    )
    d.rectangle([dx - 9, dy - 12, dx + 9, dy], fill=(47, 224, 106, 230))
    d.polygon([(dx, dy + 26), (dx - 11, dy + 8), (dx + 11, dy + 8)], fill=(47, 224, 106, 240))

    composed = Image.alpha_composite(base.convert("RGBA"), ov)

    # Crop 3:4 around route
    xs = [to_xy(lat, lon)[0] for lon, lat in main_coords] + [ox, dx]
    ys = [to_xy(lat, lon)[1] for lon, lat in main_coords] + [oy, dy]
    if alt_coords:
        xs += [to_xy(lat, lon)[0] for lon, lat in alt_coords]
        ys += [to_xy(lat, lon)[1] for lon, lat in alt_coords]
    pad = 210
    left, right = min(xs) - pad, max(xs) + pad
    top, bottom = min(ys) - pad, max(ys) + pad
    bw, bh = right - left, bottom - top
    ratio = 3 / 4
    if bw / bh > ratio:
        nh = bw / ratio
        e = (nh - bh) / 2
        top -= e
        bottom += e
    else:
        nw = bh * ratio
        e = (nw - bw) / 2
        left -= e
        right += e
    left, top, right, bottom = map(
        int,
        [
            max(0, left),
            max(0, top),
            min(composed.width, right),
            min(composed.height, bottom),
        ],
    )
    crop = composed.crop((left, top, right, bottom)).resize(
        (W_OUT, H_OUT), Image.Resampling.LANCZOS
    )

    # Cloud vignette + soft mist bands
    vig = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(100):
        a = int(200 * (i / 100) ** 2)
        vd.rectangle([i, i, W_OUT - 1 - i, H_OUT - 1 - i], outline=(0, 0, 0, a))
    for y0, a0, flip in ((0, 140, False), (H_OUT - 160, 160, True)):
        for i in range(160):
            t = i / 160
            if flip:
                t = 1 - t
            vd.line(
                [(0, y0 + i), (W_OUT, y0 + i)],
                fill=(8, 12, 20, int(a0 * (1 - t))),
            )
    crop = Image.alpha_composite(crop.convert("RGBA"), vig)

    sx = W_OUT / (right - left)
    sy = H_OUT / (bottom - top)

    def P(lat, lon):
        x, y = to_xy(lat, lon)
        return (x - left) * sx, (y - top) * sy

    font_title = load_font("/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf", 40)
    font_lg = load_font("/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf", 24)
    font_md = load_font("/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf", 18)
    font_sm = load_font("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf", 15)
    font_xs = load_font("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf", 13)

    GOLD = (242, 214, 140, 255)
    GOLD_DIM = (210, 185, 120, 235)
    GREEN = (170, 255, 200, 255)
    BLUE = (150, 185, 255, 230)

    lab = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lab)

    def text(xy, s, font, fill=GOLD, anchor="mm"):
        for ox_, oy_ in ((-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)):
            ld.text((xy[0] + ox_, xy[1] + oy_), s, font=font, fill=(0, 0, 0, 170), anchor=anchor)
        ld.text(xy, s, font=font, fill=fill, anchor=anchor)

    # --- Verified labels only (whitelist) ---
    text(P(59.9308, 30.3220), "САНКТ-ПЕТЕРБУРГ", font_title, GOLD)

    # Water
    text(P(59.9472, 30.3300), "р. Нева", font_md, GOLD_DIM)
    text(P(59.9390, 30.2995), "р. Большая Нева", font_sm, GOLD_DIM)
    text(P(59.9495, 30.3010), "р. Малая Нева", font_sm, GOLD_DIM)

    # Landmarks
    text(P(59.9512, 30.3165), "Петропавловская крепость", font_sm, GOLD)
    text(P(59.9328, 30.3061), "Исаакиевский собор", font_sm, GOLD)
    text(P(*PALACE_BRIDGE), "Дворцовый мост", font_xs, GOLD_DIM)
    # Streets on main OSRM route + key parallel streets from the screenshot
    text(P(59.9436, 30.3452), "Моховая ул.", font_md, GOLD)
    text(P(59.9418, 30.3425), "ул. Пестеля", font_sm, GOLD_DIM)
    text(P(59.9408, 30.3355), "наб. реки Мойки", font_sm, GOLD_DIM)
    text(P(59.9416, 30.3255), "Миллионная ул.", font_sm, GOLD_DIM)
    text(P(59.9425, 30.3185), "Дворцовая наб.", font_sm, GOLD_DIM)
    text(P(59.9418, 30.3055), "Университетская наб.", font_xs, GOLD_DIM)
    text(P(59.9388, 30.3480), "Литейный просп.", font_xs, GOLD_DIM)
    text(P(59.9362, 30.3185), "Невский просп.", font_md, GOLD)
    text(P(59.9335, 30.3280), "Садовая ул.", font_sm, GOLD_DIM)
    text(P(59.9405, 30.3145), "Дворцовая площадь", font_xs, GOLD_DIM)
    text(P(59.9438, 30.2870), "1-я линия В.О.", font_xs, GOLD_DIM)
    text(P(59.9522, 30.2950), "ул. Блохина", font_xs, GOLD_DIM)
    text(P(59.9530, 30.3020), "Зверинская ул.", font_xs, GOLD_DIM)
    text(P(59.9455, 30.2935), "наб. Макарова", font_xs, GOLD_DIM)
    text(P(59.9398, 30.3415), "р. Фонтанка", font_xs, GOLD_DIM)

    # Metro from screenshot — offset off the neon lines
    text(P(59.9368, 30.3125), "м. Адмиралтейская", font_xs, BLUE)
    text(P(59.9370, 30.3285), "м. Невский проспект", font_xs, BLUE)
    text(P(59.9325, 30.3360), "м. Гостиный двор", font_xs, BLUE)
    text(P(59.9525, 30.2885), "м. Спортивная", font_xs, BLUE)

    # Endpoint callouts
    dxp, dyp = P(*DEST)
    text((dxp, dyp - 42), "Петербургский Мистериум", font_lg, GREEN)
    text((dxp, dyp - 20), "Биржевой проезд, 2", font_xs, GOLD_DIM)

    oxp, oyp = P(*ORIGIN)
    text((oxp + 8, oyp + 30), "старт · Моховая ул.", font_xs, (255, 230, 150, 255))

    # Screenshot ETA (not raw OSRM)
    text((540, 1378), "3 км  ·  8 мин", font_lg, GOLD)
    text((540, 1408), "Моховая ул.  →  Петербургский Мистериум", font_xs, GOLD_DIM)

    # Legend chips
    text((90, 70), "маршрут", font_xs, (47, 224, 106, 255), anchor="lm")
    text((90, 92), "альтернатива", font_xs, (180, 150, 255, 255), anchor="lm")

    final = Image.alpha_composite(crop, lab).convert("RGB")
    final = ImageEnhance.Contrast(final).enhance(1.05)

    out = OUT_DIR / "mysterium-route-map.jpg"
    final.save(out, "JPEG", quality=93)
    ART_DIR.mkdir(parents=True, exist_ok=True)
    final.save(ART_DIR / "mysterium-route-map.jpg", "JPEG", quality=93)
    crop.convert("RGB").save(OUT_DIR / "geo-base-nolabels.jpg", "JPEG", quality=90)

    meta = {
        "origin": {"name": "Моховая ул.", "lat": ORIGIN[0], "lon": ORIGIN[1]},
        "destination": {
            "name": "Петербургский Мистериум",
            "address": "Биржевой проезд, 2",
            "lat": DEST[0],
            "lon": DEST[1],
        },
        "route_osrm_km": round(main_route["distance"] / 1000, 2),
        "route_osrm_min": round(main_route["duration"] / 60, 1),
        "poster_caption": "3 км · 8 мин",
        "streets_on_main_route": [
            "Моховая ул.",
            "ул. Пестеля",
            "наб. реки Мойки",
            "Аптекарский пер.",
            "Миллионная ул.",
            "Мраморный пер.",
            "Дворцовая наб.",
            "Дворцовый мост",
            "Университетская наб.",
            "Таможенный пер.",
            "Биржевой проезд",
        ],
        "streets_on_alt_route": [
            "Садовая ул.",
            "Невский просп.",
            "Дворцовая площадь",
            "Дворцовый мост",
        ],
        "labels": [
            "САНКТ-ПЕТЕРБУРГ",
            "р. Нева",
            "р. Большая Нева",
            "р. Малая Нева",
            "р. Фонтанка",
            "Петропавловская крепость",
            "Исаакиевский собор",
            "Дворцовый мост",
            "Дворцовая площадь",
            "Моховая ул.",
            "ул. Пестеля",
            "наб. реки Мойки",
            "Миллионная ул.",
            "Дворцовая наб.",
            "Университетская наб.",
            "Литейный просп.",
            "Невский просп.",
            "Садовая ул.",
            "Биржевой проезд, 2",
            "наб. Макарова",
            "1-я линия В.О.",
            "ул. Блохина",
            "Зверинская ул.",
            "м. Адмиралтейская",
            "м. Невский проспект",
            "м. Гостиный двор",
            "м. Спортивная",
            "Петербургский Мистериум",
        ],
    }
    (OUT_DIR / "map-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("saved", out)


if __name__ == "__main__":
    main()
