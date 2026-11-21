#!/usr/bin/env python3
"""Generate technical PDF schematics for a 50\" TV table enclosure."""

from pathlib import Path

from reportlab.lib.colors import Color, black, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent / "tv-table-box-schematics.pdf"
W, H = A4

INK = Color(0.12, 0.12, 0.12)
MUTED = Color(0.40, 0.40, 0.40)
ACCENT = Color(0.10, 0.35, 0.55)
LIGHT = Color(0.92, 0.94, 0.96)
RULE = Color(0.75, 0.75, 0.75)


def register_fonts() -> tuple[str, str]:
    candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/freefont/FreeSans.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
    ]
    for regular, bold in candidates:
        if Path(regular).exists() and Path(bold).exists():
            pdfmetrics.registerFont(TTFont("Body", regular))
            pdfmetrics.registerFont(TTFont("BodyBold", bold))
            return "Body", "BodyBold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_B = register_fonts()


def header(c: canvas.Canvas, title: str, page: int, total: int = 4) -> None:
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.line(18 * mm, H - 14 * mm, W - 18 * mm, H - 14 * mm)
    c.setFillColor(INK)
    c.setFont(FONT_B, 13)
    c.drawString(18 * mm, H - 11 * mm, title)
    c.setFont(FONT, 9)
    c.setFillColor(MUTED)
    c.drawRightString(W - 18 * mm, H - 11 * mm, f"{page} / {total}")
    c.setFillColor(INK)


def footer(c: canvas.Canvas, note: str) -> None:
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(18 * mm, 14 * mm, W - 18 * mm, 14 * mm)
    c.setFont(FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(18 * mm, 9 * mm, note)
    c.setFillColor(INK)


def dim_h(c: canvas.Canvas, x1: float, x2: float, y: float, label: str) -> None:
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    c.setLineWidth(0.7)
    c.line(x1, y, x2, y)
    c.line(x1, y - 2 * mm, x1, y + 2 * mm)
    c.line(x2, y - 2 * mm, x2, y + 2 * mm)
    c.setFont(FONT, 8)
    c.drawCentredString((x1 + x2) / 2, y + 2.5 * mm, label)


def dim_v(c: canvas.Canvas, x: float, y1: float, y2: float, label: str) -> None:
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    c.setLineWidth(0.7)
    c.line(x, y1, x, y2)
    c.line(x - 2 * mm, y1, x + 2 * mm, y1)
    c.line(x - 2 * mm, y2, x + 2 * mm, y2)
    c.saveState()
    c.translate(x - 3 * mm, (y1 + y2) / 2)
    c.rotate(90)
    c.setFont(FONT, 8)
    c.drawCentredString(0, 0, label)
    c.restoreState()


def page1_overview(c: canvas.Canvas) -> None:
    header(c, "ТВ 50″ → стол: общий вид", 1)
    footer(c, "Вариант А: съёмный фартук + юбка на существующей мобильной стойке")

    c.setFont(FONT_B, 11)
    c.drawString(18 * mm, H - 24 * mm, "Идея")
    c.setFont(FONT, 9.5)
    lines = [
        "Стойку оставляем — она несёт вес ТВ и даёт колёса. Короб — лёгкая мебельная «рубашка».",
        "Экран лежит горизонтально (вверх). Рама вокруг ТВ + юбка вниз прячут корпус, VESA и кабели.",
        "Короб не опирается на матрицу и не стоит на полу: крепится хомутами/уголками к трубам стойки.",
    ]
    y = H - 30 * mm
    for line in lines:
        c.drawString(18 * mm, y, line)
        y -= 5 * mm

    # Clean orthographic 3/4 table drawing (manual coordinates)
    def poly(pts, fill=None, stroke=INK, width=1.2):
        path = c.beginPath()
        path.moveTo(*pts[0])
        for p in pts[1:]:
            path.lineTo(*p)
        path.close()
        c.setStrokeColor(stroke)
        c.setLineWidth(width)
        if fill is not None:
            c.setFillColor(fill)
            c.drawPath(path, fill=1, stroke=1)
        else:
            c.drawPath(path, fill=0, stroke=1)

    # Box top parallelogram
    # front-left, front-right, back-right, back-left
    T = [
        (40 * mm, 145 * mm),
        (155 * mm, 145 * mm),
        (175 * mm, 175 * mm),
        (60 * mm, 175 * mm),
    ]
    # Skirt front face
    F = [
        (40 * mm, 145 * mm),
        (155 * mm, 145 * mm),
        (155 * mm, 120 * mm),
        (40 * mm, 120 * mm),
    ]
    # Skirt right face
    R = [
        (155 * mm, 145 * mm),
        (175 * mm, 175 * mm),
        (175 * mm, 150 * mm),
        (155 * mm, 120 * mm),
    ]
    poly(F, fill=LIGHT)
    poly(R, fill=Color(0.84, 0.88, 0.91))
    poly(T, fill=white)

    # Screen inset (shrink top quad)
    def lerp(a, b, t):
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t

    S = [
        lerp(lerp(T[0], T[1], 0.06), lerp(T[3], T[2], 0.06), 0.08),
        lerp(lerp(T[0], T[1], 0.94), lerp(T[3], T[2], 0.94), 0.08),
        lerp(lerp(T[0], T[1], 0.94), lerp(T[3], T[2], 0.94), 0.92),
        lerp(lerp(T[0], T[1], 0.06), lerp(T[3], T[2], 0.06), 0.92),
    ]
    poly(S, fill=Color(0.16, 0.16, 0.18), stroke=ACCENT, width=1.5)

    # Poles
    c.setStrokeColor(Color(0.25, 0.25, 0.27))
    c.setLineWidth(4)
    c.line(92 * mm, 120 * mm, 92 * mm, 62 * mm)
    c.line(108 * mm, 128 * mm, 108 * mm, 68 * mm)

    # Base (H-ish)
    poly(
        [
            (55 * mm, 62 * mm),
            (145 * mm, 62 * mm),
            (155 * mm, 72 * mm),
            (65 * mm, 72 * mm),
        ],
        fill=Color(0.22, 0.22, 0.24),
        stroke=MUTED,
    )
    # Casters
    c.setFillColor(Color(0.15, 0.15, 0.15))
    for cx, cy in [(60 * mm, 58 * mm), (140 * mm, 58 * mm), (70 * mm, 74 * mm), (150 * mm, 74 * mm)]:
        c.circle(cx, cy, 2.2 * mm, fill=1, stroke=0)

    # Leader lines + labels
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.9)
    c.line(28 * mm, 168 * mm, 55 * mm, 168 * mm)
    c.line(55 * mm, 168 * mm, 62 * mm, 160 * mm)
    c.setFillColor(ACCENT)
    c.setFont(FONT_B, 9)
    c.drawString(18 * mm, 170 * mm, "Рамка-фартук")
    c.setFont(FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(18 * mm, 164 * mm, "вровень с экраном")

    c.setStrokeColor(ACCENT)
    c.line(178 * mm, 135 * mm, 195 * mm, 135 * mm)
    c.setFillColor(ACCENT)
    c.setFont(FONT_B, 9)
    c.drawString(178 * mm, 138 * mm, "Юбка 14–18 см")
    c.setFont(FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(178 * mm, 131 * mm, "прячет корпус + VESA")

    c.setStrokeColor(ACCENT)
    c.line(118 * mm, 58 * mm, 145 * mm, 52 * mm)
    c.setFillColor(ACCENT)
    c.setFont(FONT_B, 9)
    c.drawString(147 * mm, 50 * mm, "Стойка + колёса")
    c.setFont(FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(147 * mm, 45 * mm, "(как есть)")

    # Outer size callouts near drawing
    c.setFont(FONT, 8)
    c.setFillColor(ACCENT)
    c.drawString(70 * mm, 182 * mm, "≈ 118 × 70 см")

    # Key dims callout box
    c.setStrokeColor(RULE)
    c.setFillColor(LIGHT)
    c.setLineWidth(0.8)
    c.roundRect(18 * mm, 18 * mm, W - 36 * mm, 22 * mm, 3 * mm, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont(FONT_B, 9)
    c.drawString(22 * mm, 32 * mm, "Ориентиры (уточнить замером вашего ТВ)")
    c.setFont(FONT, 8.5)
    c.drawString(22 * mm, 25 * mm, "ТВ ≈ 112 × 64 см  ·  стол ≈ 118 × 70 см  ·  фартук 14–18 см  ·  высота ≈ 75 см  ·  зазор выреза +2–4 мм")

    c.showPage()


def page2_cutaway(c: canvas.Canvas) -> None:
    header(c, "Разрез сбоку — конструкция", 2)
    footer(c, "Несущая нагрузка только на стойке; короб — облицовка")

    # Side cutaway drawing (scale ~1:10 → 1cm = 1mm on paper roughly for height parts)
    # Use mm on page directly as cm of object / 1.1
    left = 35 * mm
    floor_y = 35 * mm
    scale = 1.05  # 1 cm real ≈ 1.05 mm page? better: 1cm = 2.2mm
    s = 2.0  # mm page per cm real

    def X(cm):
        return left + cm * s

    def Y(cm):
        return floor_y + cm * s

    # Floor
    c.setStrokeColor(RULE)
    c.setLineWidth(1)
    c.line(20 * mm, floor_y, W - 20 * mm, floor_y)
    c.setFont(FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(20 * mm, floor_y - 5 * mm, "пол")

    # Stand base
    c.setFillColor(Color(0.22, 0.22, 0.24))
    c.rect(X(15), Y(0), (50) * s, 2.5 * s, fill=1, stroke=0)
    # wheels
    for wx in (18, 58):
        c.circle(X(wx), Y(0), 1.2 * s, fill=1, stroke=0)

    # Poles
    c.setFillColor(Color(0.18, 0.18, 0.2))
    c.rect(X(36), Y(2.5), 2.2 * s, 56 * s, fill=1, stroke=0)
    c.rect(X(41), Y(2.5), 2.2 * s, 56 * s, fill=1, stroke=0)

    # VESA plate
    c.setFillColor(Color(0.30, 0.30, 0.32))
    c.rect(X(32), Y(58), 16 * s, 3 * s, fill=1, stroke=0)

    # TV body (underside thickness)
    c.setFillColor(Color(0.35, 0.35, 0.38))
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.rect(X(4), Y(61), 70 * s, 5 * s, fill=1, stroke=1)
    # Screen surface
    c.setFillColor(Color(0.12, 0.12, 0.14))
    c.rect(X(4), Y(66), 70 * s, 1.2 * s, fill=1, stroke=1)

    # Apron / skirt (highlighted)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.setFillColor(Color(0.82, 0.90, 0.96))
    # left wall
    c.rect(X(1), Y(55), 3 * s, 13 * s, fill=1, stroke=1)
    # right wall
    c.rect(X(74), Y(55), 3 * s, 13 * s, fill=1, stroke=1)
    # top frame lips
    c.rect(X(1), Y(67.2), 3 * s, 1.5 * s, fill=1, stroke=1)
    c.rect(X(74), Y(67.2), 3 * s, 1.5 * s, fill=1, stroke=1)
    # top rails over bezel sides (overhang)
    c.setLineWidth(1.5)
    c.line(X(1), Y(68.5), X(4), Y(68.5))
    c.line(X(74), Y(68.5), X(77), Y(68.5))

    # Clamps
    c.setFillColor(ACCENT)
    c.circle(X(37.1), Y(57), 1.4 * s, fill=1, stroke=0)
    c.circle(X(42.1), Y(57), 1.4 * s, fill=1, stroke=0)

    # Airflow arrows
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    c.setLineWidth(1)
    for ax in (20, 30, 50, 60):
        c.line(X(ax), Y(55), X(ax), Y(48))
        c.line(X(ax), Y(48), X(ax) - 1.5 * s, Y(50))
        c.line(X(ax), Y(48), X(ax) + 1.5 * s, Y(50))
    c.setFont(FONT, 8)
    c.drawString(X(22), Y(44), "вентиляция вниз (низ юбки открыт)")

    # Dimension lines
    dim_h(c, X(1), X(77), Y(74), "≈ 118 см (наружу)")
    dim_h(c, X(4), X(74), Y(72), "≈ 112 см (ТВ)")
    dim_v(c, X(82), Y(55), Y(68.7), "14–18 см")
    dim_v(c, X(-2), Y(0), Y(68.7), "≈ 75 см")

    # Callouts
    c.setFillColor(INK)
    c.setFont(FONT_B, 9)
    c.drawString(18 * mm, H - 26 * mm, "Узлы")
    items = [
        "1. Экран вверх — верх рамы вровень со стеклом или −1…2 мм",
        "2. Юбка закрывает толщину ТВ + кронштейн",
        "3. Хомуты/уголки на трубы — короб висит на стойке",
        "4. Низ открыт + щель 15–20 мм или перфорация Ø8–12",
        "5. Кабели вдоль стоек; люк 10×15 см в короткой стенке",
    ]
    y = H - 32 * mm
    c.setFont(FONT, 9)
    for it in items:
        c.drawString(18 * mm, y, it)
        y -= 5 * mm

    c.showPage()


def page3_plans(c: canvas.Canvas) -> None:
    header(c, "Чертежи раскроя (вид сверху и детали)", 3)
    footer(c, "Размеры ориентировочные — перед раскроем замерить корпус ТВ")

    # Top view of frame
    c.setFont(FONT_B, 11)
    c.setFillColor(INK)
    c.drawString(18 * mm, H - 24 * mm, "1. Вид сверху — рама-столешница")

    ox, oy = 35 * mm, 145 * mm
    # outer 118x70 at scale 1.1 mm/cm
    s = 1.15
    ow, od = 118 * s, 70 * s
    iw, id_ = 112.4 * s, 64.4 * s  # with clearance
    mx = (ow - iw) / 2
    my = (od - id_) / 2

    c.setStrokeColor(INK)
    c.setFillColor(LIGHT)
    c.setLineWidth(1.4)
    c.rect(ox, oy, ow, od, fill=1, stroke=1)
    c.setFillColor(Color(0.15, 0.15, 0.17))
    c.rect(ox + mx, oy + my, iw, id_, fill=1, stroke=1)

    # poles indication
    c.setFillColor(MUTED)
    c.circle(ox + ow / 2 - 8 * s, oy + od / 2, 2.2, fill=1, stroke=0)
    c.circle(ox + ow / 2 + 8 * s, oy + od / 2, 2.2, fill=1, stroke=0)

    dim_h(c, ox, ox + ow, oy + od + 8 * mm, "118 см")
    dim_h(c, ox + mx, ox + mx + iw, oy - 6 * mm, "112 + 2…4 мм")
    dim_v(c, ox + ow + 8 * mm, oy, oy + od, "70 см")
    dim_v(c, ox - 8 * mm, oy + my, oy + my + id_, "64 + 2…4 мм")

    c.setFont(FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(ox, oy + od + 14 * mm, "тёмное поле = вырез под ТВ; светлая полоса = рамка ≈ 3 см")

    # Exploded panels
    c.setFillColor(INK)
    c.setFont(FONT_B, 11)
    c.drawString(18 * mm, 118 * mm, "2. Детали раскроя (фанера 18 мм)")

    panels = [
        ("A", "Рама верх (с вырезом)", "118 × 70", "1 шт"),
        ("B", "Стенка длинная", "118 × 16", "2 шт"),
        ("C", "Стенка короткая", "66.4 × 16*", "2 шт"),
        ("D", "Поперечина крепления", "≈ 40 × 8", "1–2 шт"),
    ]
    c.setFont(FONT_B, 8.5)
    c.setFillColor(MUTED)
    headers = ["", "Деталь", "Размер, см", "Кол-во"]
    xs = [18 * mm, 28 * mm, 105 * mm, 150 * mm]
    y = 110 * mm
    for i, htxt in enumerate(headers):
        c.drawString(xs[i], y, htxt)
    c.setStrokeColor(RULE)
    c.line(18 * mm, y - 2 * mm, W - 18 * mm, y - 2 * mm)
    c.setFont(FONT, 9)
    c.setFillColor(INK)
    y -= 8 * mm
    for code, name, size, qty in panels:
        c.setFont(FONT_B, 9)
        c.setFillColor(ACCENT)
        c.drawString(xs[0], y, code)
        c.setFont(FONT, 9)
        c.setFillColor(INK)
        c.drawString(xs[1], y, name)
        c.drawString(xs[2], y, size)
        c.drawString(xs[3], y, qty)
        y -= 7 * mm

    c.setFont(FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(18 * mm, y - 2 * mm, "* короткие стенки между длинными (внутренний размер = 70 − 2×18 мм)")

    # Hatch note
    c.setFillColor(INK)
    c.setFont(FONT_B, 10)
    c.drawString(18 * mm, 55 * mm, "3. Люк и вентиляция")
    c.setFont(FONT, 9)
    notes = [
        "• Люк 10 × 15 см в одной короткой стенке (со стороны портов HDMI/питания) или съёмная панель.",
        "• Нижний край юбки: непрерывная щель 15–20 мм ИЛИ ряд отверстий Ø8–12 мм с шагом 25–30 мм.",
        "• Не закрывать вентиляционные решётки на тыле ТВ сплошным дном.",
        "• Опционально: оргстекло 4–6 мм / закалённое 6 мм — только на раму, не на пиксели.",
    ]
    y = 48 * mm
    for n in notes:
        c.drawString(18 * mm, y, n)
        y -= 5.5 * mm

    c.showPage()


def page4_bom(c: canvas.Canvas) -> None:
    header(c, "Материалы, крепёж, порядок сборки", 4)
    footer(c, "PDF: tv-table-box-schematics.pdf")

    c.setFont(FONT_B, 11)
    c.setFillColor(INK)
    c.drawString(18 * mm, H - 24 * mm, "BOM — вариант А (фартук на стойке)")

    rows = [
        ("Фанера берёза 15–18 мм", "1 лист 1525×1525 (или раскрой)", "Рама + 4 стенки"),
        ("Уголок стальной 30×30", "4–6 шт", "К стойке изнутри юбки"),
        ("Хомуты / U-болты на трубы", "4 шт", "Не сверлить ТВ"),
        ("Краска / масло / HPL", "~1.2 м²", "Снаружи"),
        ("Оргстекло 5 мм (опц.)", "118 × 70 см", "Только при касаниях"),
        ("Винты / конфирматы", "набор", "Сборка короба"),
        ("Ножки-дистанцы / шайбы", "по месту", "Если стекло сверху"),
    ]

    y = H - 32 * mm
    c.setFont(FONT_B, 8)
    c.setFillColor(MUTED)
    for i, htxt in enumerate(["Позиция", "Кол-во / размер", "Примечание"]):
        c.drawString([18, 85, 140][i] * mm, y, htxt)
    c.setStrokeColor(RULE)
    c.line(18 * mm, y - 2 * mm, W - 18 * mm, y - 2 * mm)
    y -= 8 * mm
    c.setFont(FONT, 9)
    c.setFillColor(INK)
    for a, b, d in rows:
        c.drawString(18 * mm, y, a)
        c.drawString(85 * mm, y, b)
        c.drawString(140 * mm, y, d)
        y -= 7 * mm

    y -= 4 * mm
    c.setFont(FONT_B, 11)
    c.drawString(18 * mm, y, "Порядок сборки")
    y -= 7 * mm
    steps = [
        "1. Замерить корпус ТВ (Ш×В), толщину с кронштейном, шаг труб стойки, расположение портов.",
        "2. Выставить высоту стойки (~75 см до плоскости экрана).",
        "3. Собрать раму A с вырезом; прикрутить стенки B и C → короб без дна.",
        "4. Сделать люк и вентиляцию; покрасить/отделать снаружи.",
        "5. Надеть короб сверху на горизонтальный ТВ; зафиксировать уголками + хомутами к трубам.",
        "6. Проложить кабели; проверить зазоры — рама не должна давить на экран.",
        "7. (Опц.) Уложить защитное стекло на дистанционные прокладки по периметру рамы.",
    ]
    c.setFont(FONT, 9)
    for st in steps:
        c.drawString(18 * mm, y, st)
        y -= 6 * mm

    y -= 3 * mm
    c.setStrokeColor(ACCENT)
    c.setFillColor(Color(0.93, 0.96, 0.98))
    c.setLineWidth(1.2)
    c.roundRect(18 * mm, 22 * mm, W - 36 * mm, 42 * mm, 3 * mm, fill=1, stroke=1)
    c.setFillColor(ACCENT)
    c.setFont(FONT_B, 10)
    c.drawString(22 * mm, 54 * mm, "Важно")
    c.setFillColor(INK)
    c.setFont(FONT, 9)
    warns = [
        "• Короб и стекло не опираются на матрицу — только на раму / стойку.",
        "• Без вентиляции снизу возможен перегрев (тыл ТВ теперь внизу).",
        "• Альтернатива «полный постамент до пола» — только если нужен монолит без видимых колёс.",
        "• Материал №1: фанера 18 мм; МДФ — бюджет; алюминий 20×20 + панели — студийный вид.",
    ]
    yy = 46 * mm
    for wline in warns:
        c.drawString(22 * mm, yy, wline)
        yy -= 5.5 * mm

    c.showPage()


def main() -> None:
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle("Короб-стол для ТВ 50″ — схемы")
    c.setAuthor("vasilevskii23")
    page1_overview(c)
    page2_cutaway(c)
    page3_plans(c)
    page4_bom(c)
    c.save()
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
