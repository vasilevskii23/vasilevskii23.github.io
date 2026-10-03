#!/usr/bin/env python3
"""КРУЖИМ Brand Positioning 2026 — PPTX + PDF from source brand book."""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import pymupdf as fitz

ROOT = Path(__file__).resolve().parent
LOGO = ROOT / "assets" / "logo.png"
SRC_PDF = Path("/home/ubuntu/.cursor/projects/workspace/uploads/_______________________________4289.pdf")

NAVY = RGBColor(0x0D, 0x1F, 0x5C)
BLUE = RGBColor(0x1C, 0x42, 0x99)
BLUE_MID = RGBColor(0x2A, 0x5B, 0xC4)
SOFT = RGBColor(0x79, 0x95, 0xCC)
BG = RGBColor(0xF0, 0xF5, 0xFF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x4A, 0x5F, 0x8F)
ORANGE = RGBColor(0xE8, 0x7A, 0x2E)
AMBER = RGBColor(0xD4, 0x92, 0x3F)
GREEN = RGBColor(0x16, 0xA2, 0x4A)
DARK = RGBColor(0x0C, 0x1A, 0x52)
CARD = RGBColor(0xEA, 0xF0, 0xFF)


def set_run(run, size=16, bold=False, color=NAVY, name="Arial"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def rect(slide, l, t, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    fill(s, color)
    return s


def round_rect(slide, l, t, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    fill(s, color)
    try:
        s.adjustments[0] = 0.12
    except Exception:
        pass
    return s


def text(slide, l, t, w, h, value, size=16, bold=False, color=NAVY, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = value
    set_run(run, size=size, bold=bold, color=color)
    return box


def logo_row(slide, section, dark=False):
    if LOGO.exists():
        slide.shapes.add_picture(str(LOGO), Inches(0.5), Inches(0.32), Inches(0.38), Inches(0.38))
    text(slide, Inches(1.0), Inches(0.34), Inches(3), Inches(0.35),
         "КРУЖИМ", size=14, bold=True, color=WHITE if dark else NAVY)
    text(slide, Inches(7.5), Inches(0.38), Inches(5.3), Inches(0.3),
         section.upper(), size=11, bold=True, color=SOFT if not dark else RGBColor(0xB8, 0xC8, 0xE8),
         align=PP_ALIGN.RIGHT)


def footer(slide, n, total=6, dark=False):
    c = RGBColor(0x9A, 0xB0, 0xD8) if dark else SOFT
    text(slide, Inches(0.5), Inches(7.05), Inches(7), Inches(0.3),
         "КРУЖИМ · Brand book" + (" · кружим.рф" if n == total else ""), size=11, color=c)
    text(slide, Inches(11.6), Inches(7.05), Inches(1.2), Inches(0.3),
         f"{n:02d}", size=11, color=c, align=PP_ALIGN.RIGHT)


def blank(prs, dark=False):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fill(slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height),
         DARK if dark else BG)
    return slide


def build_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1 Cover
    s = blank(prs, dark=True)
    rect(s, Inches(8.8), 0, Inches(4.6), Inches(7.5), BLUE_MID)
    logo_row(s, "Brand Positioning · 2026", dark=True)
    text(s, Inches(0.5), Inches(1.7), Inches(10), Inches(0.35),
         "BRAND POSITIONING · 2026", size=12, bold=True, color=SOFT)
    text(s, Inches(0.5), Inches(2.3), Inches(11), Inches(0.7),
         "Кружки СПб — заявка уходит,", size=34, bold=True, color=WHITE)
    round_rect(s, Inches(0.5), Inches(3.15), Inches(6.4), Inches(0.75), ORANGE)
    text(s, Inches(0.65), Inches(3.3), Inches(6.1), Inches(0.45),
         "организатор звонит", size=28, bold=True, color=WHITE)
    text(s, Inches(0.5), Inches(4.3), Inches(9), Inches(1.0),
         "Позиционирование бренда: территория, сильные стороны,\nпреимущества и почему родители выбирают КРУЖИМ.",
         size=15, color=SOFT)
    round_rect(s, Inches(0.5), Inches(5.6), Inches(5.4), Inches(0.5), DARK)
    # outline-ish pill
    text(s, Inches(0.7), Inches(5.68), Inches(5.1), Inches(0.35),
         "Городской стол записи в детские занятия", size=13, bold=True, color=WHITE)
    text(s, Inches(0.5), Inches(6.4), Inches(6), Inches(0.3),
         "кружим.рф · Санкт-Петербург", size=12, color=SOFT)
    footer(s, 1, dark=True)

    # 2 Territory
    s = blank(prs)
    logo_row(s, "Позиционирование")
    text(s, Inches(0.5), Inches(0.9), Inches(12), Inches(0.5),
         "Территория бренда", size=28, bold=True, color=NAVY)
    text(s, Inches(0.5), Inches(1.45), Inches(12), Inches(0.35),
         "Не «ещё один каталог», а сервис, где заявка заканчивается звонком организатора.",
         size=14, color=MUTED)
    round_rect(s, Inches(0.5), Inches(1.95), Inches(12.3), Inches(3.35), BLUE)
    lines = [
        ("Для", "родителей в Санкт-Петербурге"),
        ("которые", "устали искать кружок по чатам, сайтам и «навигаторам»"),
        ("КРУЖИМ —", "городской стол записи: возраст + район → короткий список → звонок"),
        ("потому что", "муниципальные и частные — в одном каталоге, заявка уходит партнёру"),
        ("в отличие от", "Навигатора ДО / Familypass / чата — бюрократия, слот или тишина"),
    ]
    y = 2.15
    for k, v in lines:
        text(s, Inches(0.75), Inches(y), Inches(1.7), Inches(0.3), k, size=12, bold=True, color=AMBER)
        text(s, Inches(2.5), Inches(y), Inches(9.9), Inches(0.35), v, size=13, color=WHITE)
        y += 0.48
    text(s, Inches(0.75), Inches(4.75), Inches(11.5), Inches(0.35),
         "«Кружки СПб — заявка уходит, организатор звонит.»", size=14, bold=True, color=WHITE)
    text(s, Inches(0.5), Inches(5.5), Inches(4), Inches(0.3), "НЕ ДЛЯ КОГО", size=11, bold=True, color=SOFT)
    for i, t in enumerate([
        "Не маркетплейс разовых слотов",
        "Не гос. сертификатный портал",
        "Не всероссийский «всё для детей»",
    ]):
        x = 0.5 + i * 4.15
        round_rect(s, Inches(x), Inches(5.85), Inches(3.95), Inches(0.95), WHITE)
        text(s, Inches(x + 0.2), Inches(5.95), Inches(1), Inches(0.3), f"0{i+1}", size=14, bold=True, color=BLUE_MID)
        text(s, Inches(x + 0.2), Inches(6.3), Inches(3.5), Inches(0.4), t, size=12, bold=True, color=NAVY)
    footer(s, 2)

    # 3 Strengths
    s = blank(prs)
    logo_row(s, "Сильные стороны")
    text(s, Inches(0.5), Inches(0.9), Inches(12), Inches(0.45),
         "Сильные стороны продукта", size=28, bold=True, color=NAVY)
    text(s, Inches(0.5), Inches(1.4), Inches(12), Inches(0.35),
         "То, что уже есть в продукте и защищает позиционирование — не обещания «на бумаге».",
         size=14, color=MUTED)
    items = [
        ("1", "Петля доверия: заявка → звонок", "Родитель оставляет заявку, партнёр получает лид и перезванивает."),
        ("2", "Муниципальное и частное в одном окне", "Бесплатные гос. кружки с меткой и платные школы рядом."),
        ("3", "Короткий список, не бесконечная лента", "Возраст + район (+ карта) сразу сужают выбор."),
        ("4", "Модерация партнёров", "Pending → active: не объявления с улицы."),
        ("5", "Глубина СПб, а не ширина страны", "Фокус на одном городе вместо гонки числом занятий."),
    ]
    y = 1.9
    for n, title, desc in items:
        oval = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.55), Inches(y + 0.05), Inches(0.38), Inches(0.38))
        fill(oval, BLUE)
        text(s, Inches(0.55), Inches(y + 0.1), Inches(0.38), Inches(0.3), n, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        text(s, Inches(1.15), Inches(y), Inches(11.5), Inches(0.28), title, size=14, bold=True, color=NAVY)
        text(s, Inches(1.15), Inches(y + 0.32), Inches(11.5), Inches(0.3), desc, size=12, color=MUTED)
        y += 0.72
    round_rect(s, Inches(0.5), Inches(5.7), Inches(12.3), Inches(1.05), RGBColor(0xFF, 0xF0, 0xE4))
    text(s, Inches(0.75), Inches(5.85), Inches(11.8), Inches(0.25),
         "Ключевой враг бренда", size=12, bold=True, color=ORANGE)
    text(s, Inches(0.75), Inches(6.2), Inches(11.8), Inches(0.4),
         "Пустые заявки, мёртвые объявления и чаты без подтверждения. Против хаоса поиска — за живой ответ.",
         size=13, color=NAVY)
    footer(s, 3)

    # 4 Benefits
    s = blank(prs)
    logo_row(s, "Преимущества")
    text(s, Inches(0.5), Inches(0.85), Inches(12), Inches(0.4),
         "Преимущества для родителей", size=26, bold=True, color=NAVY)
    benefits = [
        ("Экономия вечеров", "Один заход вместо десяти вкладок, чатов мам и «уточните у администратора»."),
        ("Понятный следующий шаг", "Не «сохранить в избранное», а заявка с ожидаемым звонком организатора."),
        ("Честные метки", "Муниципальный / платный, возраст, район, цена или «Бесплатно»."),
        ("Доверие к каталогу", "Партнёры проходят регистрацию и модерацию — не анонимная доска."),
    ]
    for i, (title, desc) in enumerate(benefits):
        x = 0.5 + (i % 2) * 6.4
        y = 1.4 + (i // 2) * 1.25
        round_rect(s, Inches(x), Inches(y), Inches(6.15), Inches(1.1), CARD)
        text(s, Inches(x + 0.2), Inches(y + 0.15), Inches(5.7), Inches(0.3), title, size=14, bold=True, color=NAVY)
        text(s, Inches(x + 0.2), Inches(y + 0.5), Inches(5.7), Inches(0.5), desc, size=12, color=MUTED)
    text(s, Inches(0.5), Inches(4.0), Inches(12), Inches(0.3),
         "ПРЕИМУЩЕСТВА ДЛЯ ПАРТНЁРОВ", size=11, bold=True, color=BLUE)
    for i, (title, desc) in enumerate([
        ("Заявки от родителей рядом", "Лиды из целевого района и возраста — не место ради галочки."),
        ("Кабинет и статусы", "Управление кружками, модерация, путь от регистрации до публикации."),
    ]):
        x = 0.5 + i * 6.4
        round_rect(s, Inches(x), Inches(4.35), Inches(6.15), Inches(0.95), WHITE)
        text(s, Inches(x + 0.2), Inches(4.45), Inches(5.7), Inches(0.25), title, size=13, bold=True, color=NAVY)
        text(s, Inches(x + 0.2), Inches(4.75), Inches(5.7), Inches(0.4), desc, size=12, color=MUTED)
    text(s, Inches(0.5), Inches(5.45), Inches(12), Inches(0.25),
         "ТРИ ОПОРЫ СООБЩЕНИЙ", size=11, bold=True, color=BLUE)
    for i, (title, desc) in enumerate([
        ("Короткий список", "Сначала возраст и район — потом варианты"),
        ("Живой ответ", "Заявка заканчивается звонком, не тишиной"),
        ("Всё честное рядом", "Муниципальное и частное — с явной меткой"),
    ]):
        x = 0.5 + i * 4.15
        round_rect(s, Inches(x), Inches(5.8), Inches(3.95), Inches(0.95), BLUE)
        text(s, Inches(x + 0.2), Inches(5.9), Inches(3.5), Inches(0.28), title, size=13, bold=True, color=WHITE)
        text(s, Inches(x + 0.2), Inches(6.25), Inches(3.5), Inches(0.4), desc, size=11, color=SOFT)
    footer(s, 4)

    # 5 Why
    s = blank(prs)
    logo_row(s, "Почему КРУЖИМ")
    text(s, Inches(0.5), Inches(0.85), Inches(12), Inches(0.4),
         "Почему КРУЖИМ, а не кто-то ещё", size=26, bold=True, color=NAVY)
    text(s, Inches(0.5), Inches(1.3), Inches(12), Inches(0.3),
         "Сравнение по главному вопросу родителя: «Мне ответят и запишут — или снова в пустоту?»",
         size=13, color=MUTED)
    rows = [
        ("Альтернатива", "Их обещание", "Слабое место", "КРУЖИМ"),
        ("Навигатор ДО", "Госреестр и сертификаты", "Бюрократия, не про быструю запись", "Живая заявка + звонок"),
        ("Familypass", "«Все секции», покупка слотов", "Ширина важнее подтверждения", "Глубина СПб + ответ"),
        ("Чаты / форумы", "«Живые советы»", "Хаос, без статуса заявки", "Структура + статус"),
        ("Google / Avito", "Найти объявление", "Мёртвые страницы", "Модерация партнёров"),
        ("Ничего не делать", "Подождать / спросить в школе", "Упущенный сезон", "Старт за вечер"),
    ]
    col_w = [2.5, 3.3, 3.7, 2.8]
    y = 1.75
    for ri, row in enumerate(rows):
        x = 0.5
        bg = BLUE if ri == 0 else (WHITE if ri % 2 else CARD)
        h = 0.55 if ri == 0 else 0.62
        for ci, (cell, w) in enumerate(zip(row, col_w)):
            rect(s, Inches(x), Inches(y), Inches(w), Inches(h), bg)
            if ri and ci == 3:
                color = ORANGE if ri == 5 else GREEN
                round_rect(s, Inches(x + 0.12), Inches(y + 0.12), Inches(w - 0.24), Inches(0.38), color)
                text(s, Inches(x + 0.12), Inches(y + 0.16), Inches(w - 0.24), Inches(0.3),
                     cell, size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
            else:
                c = WHITE if ri == 0 else NAVY
                text(s, Inches(x + 0.1), Inches(y + 0.15), Inches(w - 0.15), Inches(h - 0.15),
                     cell, size=11, bold=(ri == 0 or ci == 0), color=c)
            x += w
        y += h
    round_rect(s, Inches(0.5), Inches(5.85), Inches(12.3), Inches(0.9), RGBColor(0xFF, 0xF0, 0xE4))
    text(s, Inches(0.75), Inches(5.95), Inches(11.8), Inches(0.25), "Одной фразой", size=11, bold=True, color=ORANGE)
    text(s, Inches(0.75), Inches(6.25), Inches(11.8), Inches(0.35),
         "Другие собирают занятия. КРУЖИМ доводит до разговора с организатором.",
         size=14, bold=True, color=NAVY)
    footer(s, 5)

    # 6 Voice + proof
    s = blank(prs)
    logo_row(s, "Голос и следующий шаг")
    text(s, Inches(0.5), Inches(0.85), Inches(12), Inches(0.4),
         "Голос бренда и proof roadmap", size=26, bold=True, color=NAVY)
    round_rect(s, Inches(0.5), Inches(1.4), Inches(6.0), Inches(2.5), WHITE)
    text(s, Inches(0.7), Inches(1.55), Inches(5.5), Inches(0.3), "Как говорим", size=14, bold=True, color=NAVY)
    for i, t in enumerate([
        "Спокойно и конкретно",
        "Глаголами процесса: выбрали → оставили → перезвонили",
        "Уважаем время родителя",
        "Без сюсюканья и крика",
        "Городской тон СПб",
    ]):
        text(s, Inches(0.7), Inches(1.95 + i * 0.35), Inches(5.5), Inches(0.3), f"•  {t}", size=12, color=MUTED)
    round_rect(s, Inches(6.8), Inches(1.4), Inches(6.0), Inches(2.5), WHITE)
    text(s, Inches(7.0), Inches(1.55), Inches(5.5), Inches(0.3), "Как не говорим", size=14, bold=True, color=NAVY)
    for i, t in enumerate([
        "«Лучший выбор», «#1», «экосистема»",
        "«Инновации», пустая «забота»",
        "«Всё для детей» без фокуса",
        "Гонка числом занятий с агрегаторами",
        "Притворство гос. навигатором",
    ]):
        text(s, Inches(7.0), Inches(1.95 + i * 0.35), Inches(5.5), Inches(0.3), f"•  {t}", size=12, color=MUTED)

    round_rect(s, Inches(0.5), Inches(4.1), Inches(12.3), Inches(1.35), BLUE)
    text(s, Inches(0.75), Inches(4.2), Inches(11.8), Inches(0.25), "КРУЖИМ", size=14, bold=True, color=WHITE)
    text(s, Inches(0.75), Inches(4.5), Inches(11.8), Inches(0.3),
         "Заявка в кружок — и звонок организатора", size=16, bold=True, color=WHITE)
    text(s, Inches(0.75), Inches(4.9), Inches(8), Inches(0.25),
         "Возраст и район → муниципальные и частные занятия в СПб", size=12, color=SOFT)
    round_rect(s, Inches(9.7), Inches(4.85), Inches(2.8), Inches(0.4), ORANGE)
    text(s, Inches(9.7), Inches(4.9), Inches(2.8), Inches(0.3),
         "Подобрать кружок", size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    text(s, Inches(0.5), Inches(5.6), Inches(12), Inches(0.25),
         "ЧТО УСИЛИТЬ В ПРОДУКТЕ", size=11, bold=True, color=BLUE)
    proofs = [
        ("1", "Метрика «% заявок с ответом за 24ч»", "Сделать «живой ответ» измеримым"),
        ("2", "SLA / пауза партнёров без звонка", "Защитить доверие"),
        ("3", "Hero и партнёрский лендинг на spine", "Сообщение = продукт"),
        ("4", "Метки муниципальный / платный", "Честность каталога"),
    ]
    for i, (n, p, why) in enumerate(proofs):
        x = 0.5 + i * 3.2
        text(s, Inches(x), Inches(5.95), Inches(3.0), Inches(0.25), f"{n}. {p}", size=10, bold=True, color=NAVY)
        text(s, Inches(x), Inches(6.25), Inches(3.0), Inches(0.35), why, size=10, color=MUTED)
    footer(s, 6)

    out = ROOT / "КРУЖИМ_Brand_Positioning_2026.pptx"
    prs.save(out)
    print("PPTX:", out)
    return out


def build_pdf_from_source():
    """Export a clean presentation PDF: original 6 pages + optional landscape wrap not needed.
    Also create landscape PDF by placing each source page centered on 16:9 canvas.
    """
    if not SRC_PDF.exists():
        # fallback: use uploaded copy if present in presentation
        alt = ROOT / "source.pdf"
        src = alt if alt.exists() else None
    else:
        src = SRC_PDF

    # Copy source into presentation folder for the repo
    dest_src = ROOT / "source_brand_positioning.pdf"
    if src and src.exists():
        dest_src.write_bytes(src.read_bytes())

    # Landscape presentation PDF: each page of source on a 16:9 blue-framed slide
    doc_in = fitz.open(str(src if src and src.exists() else dest_src))
    doc_out = fitz.open()
    # 16:9 at 1920x1080 points-ish — use 960x540 for lighter file, or standard 842×473
    W, H = 960, 540
    for i, page in enumerate(doc_in):
        out = doc_out.new_page(width=W, height=H)
        # background
        out.draw_rect(fitz.Rect(0, 0, W, H), color=None, fill=(0.94, 0.96, 1.0))
        # fit portrait page into slide with margins
        margin = 18
        avail_w = W - 2 * margin
        avail_h = H - 2 * margin - 24
        pw, ph = page.rect.width, page.rect.height
        scale = min(avail_w / pw, avail_h / ph)
        tw, th = pw * scale, ph * scale
        x0 = (W - tw) / 2
        y0 = margin + 10 + (avail_h - th) / 2
        out.show_pdf_page(fitz.Rect(x0, y0, x0 + tw, y0 + th), doc_in, i)
        # footer label
        out.insert_text(
            (margin, H - 12),
            f"КРУЖИМ · Brand Positioning 2026 · {i+1:02d}/{doc_in.page_count:02d}",
            fontsize=8,
            color=(0.47, 0.58, 0.8),
        )
    out_path = ROOT / "КРУЖИМ_Brand_Positioning_2026.pdf"
    doc_out.save(out_path)
    doc_out.close()
    doc_in.close()
    print("PDF:", out_path)
    return out_path


if __name__ == "__main__":
    build_pptx()
    build_pdf_from_source()
