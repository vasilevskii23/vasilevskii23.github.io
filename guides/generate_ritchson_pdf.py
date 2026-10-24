#!/usr/bin/env python3
"""Generate Alan Ritchson training system PDF (Russian)."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = Path(__file__).resolve().parent / "Alan_Ritchson_Sistema_Trenirovok.pdf"

pdfmetrics.registerFont(TTFont("DejaVu", FONT))
pdfmetrics.registerFont(TTFont("DejaVuBold", FONT_BOLD))

NAVY = colors.HexColor("#1a2332")
STEEL = colors.HexColor("#2c3e50")
ACCENT = colors.HexColor("#c45c26")
LIGHT = colors.HexColor("#f4f0ea")
ROW_ALT = colors.HexColor("#eef2f5")
BORDER = colors.HexColor("#b8c0c8")
WHITE = colors.white


def styles():
    base = getSampleStyleSheet()
    s = {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="DejaVuBold",
            fontSize=26,
            leading=32,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontName="DejaVu",
            fontSize=12,
            leading=16,
            textColor=STEEL,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName="DejaVuBold",
            fontSize=16,
            leading=20,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="DejaVuBold",
            fontSize=12,
            leading=16,
            textColor=ACCENT,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="DejaVu",
            fontSize=9.5,
            leading=13.5,
            textColor=STEEL,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "note": ParagraphStyle(
            "note",
            fontName="DejaVu",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#5a6570"),
            alignment=TA_LEFT,
            spaceAfter=6,
            leftIndent=4,
            rightIndent=4,
        ),
        "quote": ParagraphStyle(
            "quote",
            fontName="DejaVu",
            fontSize=9,
            leading=13,
            textColor=STEEL,
            alignment=TA_LEFT,
            leftIndent=12,
            rightIndent=12,
            spaceBefore=4,
            spaceAfter=8,
            borderPadding=6,
        ),
        "cell": ParagraphStyle(
            "cell",
            fontName="DejaVu",
            fontSize=8,
            leading=11,
            textColor=STEEL,
        ),
        "cell_b": ParagraphStyle(
            "cell_b",
            fontName="DejaVuBold",
            fontSize=8,
            leading=11,
            textColor=NAVY,
        ),
        "th": ParagraphStyle(
            "th",
            fontName="DejaVuBold",
            fontSize=8,
            leading=11,
            textColor=WHITE,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="DejaVu",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#7a8490"),
            alignment=TA_CENTER,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="DejaVu",
            fontSize=9.5,
            leading=13,
            textColor=STEEL,
            leftIndent=8,
            spaceAfter=2,
        ),
    }
    return s


def P(text, style):
    return Paragraph(text, style)


def make_table(headers, rows, col_widths, s):
    data = [[P(h, s["th"]) for h in headers]]
    for row in rows:
        data.append([P(str(c), s["cell"]) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuBold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(1.8 * cm, 1.4 * cm, A4[0] - 1.8 * cm, 1.4 * cm)
    canvas.setFont("DejaVu", 7.5)
    canvas.setFillColor(colors.HexColor("#7a8490"))
    canvas.drawCentredString(
        A4[0] / 2,
        0.9 * cm,
        f"Система тренировок Алана Ричсона (Reacher)  |  стр. {doc.page}  |  не медицинская рекомендация",
    )
    canvas.restoreState()


def build():
    s = styles()
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.6 * cm,
        bottomMargin=2.0 * cm,
        title="Система тренировок Алана Ричсона (Reacher)",
        author="Research compilation",
    )
    story = []
    W = A4[0] - 3.6 * cm

    # Cover
    story.append(Spacer(1, 2.2 * cm))
    story.append(P("СИСТЕМА ТРЕНИРОВОК", s["cover_sub"]))
    story.append(P("Алана Ричсона", s["cover_title"]))
    story.append(P("(Alan Ritchson / Jack Reacher)", s["cover_sub"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(
        P(
            "Полный справочник: тренировки · диета · спортпит · витамины · распорядок дня",
            s["cover_sub"],
        )
    )
    story.append(Spacer(1, 0.8 * cm))

    meta = make_table(
        ["Параметр", "Значение"],
        [
            ["Рост", "≈ 188–190 см (6'2\"–6'3\")"],
            ["Вес (Reacher)", "≈ 106–110+ кг (235–240+ lbs)"],
            ["Набор для роли", "+13–16 кг мышц за ~8 месяцев"],
            ["Базовый возраст (на старте Reacher)", "около 40 лет"],
            ["Цель", "массa + функциональность для экшена"],
        ],
        [W * 0.38, W * 0.62],
        s,
    )
    story.append(meta)
    story.append(Spacer(1, 0.6 * cm))
    story.append(
        P(
            "<b>Важно:</b> документ собран по открытым интервью (Men's Health Gym &amp; Fridge, "
            "Men's Fitness, Generation Iron, Set For Set и др.). Часть программ в СМИ — "
            "реконструкции. Основной приоритет — прямые цитаты актёра. Это не медсовет; "
            "TRT и добавки — только после консультации с врачом.",
            s["note"],
        )
    )

    # 1. Overview principles
    story.append(P("1. Ключевые принципы системы", s["h1"]))
    story.append(
        P(
            "До роли Reacher Ричсон десятилетиями держал форму на калистенике. "
            "После кастинга перешёл на бодибилдерский сплит с высоким объёмом, "
            "короткими жёсткими сессиями и большим калорийным профицитом. "
            "Сейчас цель — не ставить рекорды, а <b>поддерживать</b> Reacher-физику "
            "максимально долго.",
            s["body"],
        )
    )
    story.append(
        P(
            "«If you're trying to bulk or add strength, put more strain on your muscles "
            "than you did yesterday.» — Alan Ritchson",
            s["quote"],
        )
    )

    principles = make_table(
        ["Принцип", "Как применяет", "Что взять себе"],
        [
            [
                "Короткие тренировки",
                "20–30 минут, но «на отказ»",
                "Интенсивность важнее длительности",
            ],
            [
                "Высокий объём",
                "15–25 повторений, суперсеты",
                "Гипертрофия без тяжёлых 1ПМ",
            ],
            [
                "Калистеника в базе",
                "Подтягивания, отжимания, брусья, пресс, спринты",
                "Оставлять как финишер 2–4×/нед.",
            ],
            [
                "Калория = калория",
                "80/20 + cookie dough / key lime pie",
                "Профицит важнее «идеальной» чистоты",
            ],
            [
                "Восстановление",
                "Сауна ~15 мин, отдых, сон",
                "Не копировать без восстановления",
            ],
        ],
        [W * 0.22, W * 0.40, W * 0.38],
        s,
    )
    story.append(principles)

    # 2. Workouts - Primary (bro split from MH / GI / SFS)
    story.append(P("2. Тренировочная программа (основной Reacher-сплит)", s["h1"]))
    story.append(
        P(
            "Наиболее согласованная версия по интервью Men's Health / Generation Iron / "
            "Set For Set: классический bro-split Пн–Пт, ~30 минут, кабели и Smith, "
            "диапазон 15–25. Кардио почти каждый день. Бойцовая хореография отдельно "
            "«убивает» кардио за 2–3 минуты — он использует это как проверку.",
            s["body"],
        )
    )

    story.append(P("Понедельник — Грудь", s["h2"]))
    story.append(
        make_table(
            ["Упражнение", "Подходы", "Повторения"],
            [
                ["Smith Incline Press", "4", "15–25"],
                ["Smith Flat Press", "4", "15–25"],
                ["Smith Decline Press", "4", "15–25"],
                ["Cable Chest Fly (низкий блок)", "3–4", "15–25"],
                ["Отжимания", "1–2", "до отказа"],
                ["HIIT кардио", "—", "≈ 20 мин"],
            ],
            [W * 0.55, W * 0.2, W * 0.25],
            s,
        )
    )
    story.append(
        P(
            "На «хороший день» — до ~100 тяжёлых жимов: сначала incline → flat → decline.",
            s["note"],
        )
    )

    story.append(P("Вторник — Спина", s["h2"]))
    story.append(
        make_table(
            ["Упражнение", "Подходы", "Повторения"],
            [
                ["Подтягивания", "4", "до отказа"],
                ["Seated / Standing Cable Row", "4", "15–25"],
                ["Lat Pulldown", "3", "15–25"],
                ["DB Single-Arm Row", "3", "15–25"],
                ["Cable Lat Extension (канат)", "3", "15–25"],
                ["Бег на дорожке", "—", "несколько км"],
            ],
            [W * 0.55, W * 0.2, W * 0.25],
            s,
        )
    )

    story.append(P("Среда — Ноги + пресс", s["h2"]))
    story.append(
        make_table(
            ["Упражнение", "Подходы", "Повторения"],
            [
                ["DB Lunges", "3", "15–25"],
                ["DB Split Squat", "3", "15–25"],
                ["Leg Extension", "3", "15–25"],
                ["Leg Curl", "3", "15–25"],
                ["Leg Raises", "3", "15–25"],
                ["Sit-ups", "3", "15–25"],
                ["Sled push / pull", "—", "≈ 10 мин"],
            ],
            [W * 0.55, W * 0.2, W * 0.25],
            s,
        )
    )
    story.append(
        P(
            "Примечание: приседы/тяги часто избегает из‑за поясницы — упор на одноногие "
            "и тренажёры.",
            s["note"],
        )
    )

    story.append(P("Четверг — Плечи", s["h2"]))
    story.append(
        make_table(
            ["Упражнение", "Подходы", "Повторения"],
            [
                ["Smith Shoulder Press", "4", "15–25"],
                ["Standing Cable Shoulder Press", "3", "15–25"],
                ["Cable Lateral Raise", "3", "15–25"],
                ["Cable Face Pull", "3", "15–25"],
                ["DB Shrugs", "3", "15–25"],
                ["HIIT", "—", "≈ 20 мин"],
            ],
            [W * 0.55, W * 0.2, W * 0.25],
            s,
        )
    )

    story.append(P("Пятница — Руки", s["h2"]))
    story.append(
        make_table(
            ["Упражнение", "Подходы", "Повторения"],
            [
                ["Суперсет: Rope Pushdown + Overhead Extension", "4", "15–25"],
                ["Rope Hammer Curl", "4", "15–25"],
                ["DB Hammer-Grip Bench Press", "4", "15–25"],
                ["DB Skull Crusher", "4", "15–25"],
                ["EZ Bar Curl (21's)", "4", "7+7+7"],
                ["EZ Overhead Triceps Extension", "4", "15–25"],
                ["Брусья (dips)", "1–2", "до отказа"],
                ["Бег", "—", "несколько км"],
            ],
            [W * 0.55, W * 0.2, W * 0.25],
            s,
        )
    )

    story.append(P("Суббота–Воскресенье", s["h2"]))
    story.append(
        P(
            "Часто активное восстановление / отдых. На съёмках — бойцовая подготовка. "
            "Домашний зал: акцент на кабели (в отелях их мало).",
            s["body"],
        )
    )

    # Calisthenics foundation
    story.append(P("3. База калистеники (20+ лет)", s["h1"]))
    story.append(
        P(
            "«These five are the core foundation for my routine…» — пять упражнений, "
            "на которых держалась форма до тяжёлого железа:",
            s["body"],
        )
    )
    story.append(
        make_table(
            ["Упражнение", "Роль"],
            [
                ["Pull-ups (подтягивания)", "Спина, бицепс, хват"],
                ["Dips (брусья)", "Грудь, трицепс, плечи"],
                ["Push-ups (отжимания)", "Жимовой объём без железа"],
                ["Sit-ups / пресс", "Кор"],
                ["Sprints (спринты)", "Ноги + кардио"],
            ],
            [W * 0.4, W * 0.6],
            s,
        )
    )
    story.append(Spacer(1, 0.25 * cm))
    story.append(P("30‑минутный AMRAP-цикл (парк / дома)", s["h2"]))
    story.append(
        make_table(
            ["Упражнение", "Повторения в круге"],
            [
                ["Подтягивания", "5"],
                ["Брусья", "10"],
                ["Отжимания", "15"],
                ["Скручивания / sit-ups", "20"],
                ["Спринт", "≈ 200 м"],
            ],
            [W * 0.5, W * 0.5],
            s,
        )
    )
    story.append(
        P(
            "Круг повторять максимальное число раз за 20–30 минут. Между станциями — "
            "спринты, затем бег домой.",
            s["note"],
        )
    )

    # Diet
    story.append(PageBreak())
    story.append(P("4. Диета и макросы", s["h1"]))
    story.append(
        P(
            "Философия близка к Reacher: «калория есть калория». На наборе — профицит "
            "важнее идеальной чистоты. На площадке ест «чище» (есть повар). Дома — "
            "80/20 + сладости, которые помогают добить калории.",
            s["body"],
        )
    )
    story.append(
        make_table(
            ["Показатель", "Bulk / подготовка", "Поддержание"],
            [
                ["Калории", "≈ 4 500 ккал/день", "≈ 4 000 ккал/день"],
                ["Белок", "≈ 240–300 г/день", "минимум ≈ 240 г"],
                ["Подход", "много мелких приёмов пищи", "интуитивно + привычки"],
                ["Правило", "80% цельные продукты / 20% «фановые»", "то же"],
                ["Алкоголь", "избегает (по ряду обзоров)", "избегает"],
            ],
            [W * 0.28, W * 0.36, W * 0.36],
            s,
        )
    )

    story.append(P("Пример дня питания (clean / on-set стиль)", s["h2"]))
    story.append(
        make_table(
            ["Приём", "Состав"],
            [
                ["Завтрак", "Куриная колбаса, яичница, тост с авокадо + протеиновый шейк"],
                ["Обед", "Бурый рис, куриная грудка, брокколи"],
                ["Перекус / поздний обед", "То же + протеиновый шейк"],
                ["Ужин", "Лосось / рыба, бурый рис, овощи на гриле"],
                ["Доп. перекусы", "Творог / греческий йогурт, дели-мясо, печенье/cookie dough"],
            ],
            [W * 0.28, W * 0.72],
            s,
        )
    )

    story.append(P("Пример «реалистичного» дня с 20% indulgence", s["h2"]))
    story.append(
        make_table(
            ["Приём", "Пример", "Зачем"],
            [
                ["Завтрак", "Яйца, овсянка, фрукты", "Белок + углеводы с утра"],
                [
                    "Обед",
                    "Сэндвич (индейка, сыр, майо) + 1–2 печенья",
                    "Лёгкие калории без стресса",
                ],
                [
                    "Шейк",
                    "Протеин + миндальное молоко + банан + шпинат + арахисовая паста + овёс + авокадо",
                    "Страховка по калориям и белку",
                ],
                [
                    "Ужин",
                    "Брискет / мясной рулет, пюре, овощи, key lime pie",
                    "Якорный калорийный приём",
                ],
                ["Перед сном", "Йогурт/творог + cookie dough", "Белок + профицит"],
            ],
            [W * 0.18, W * 0.50, W * 0.32],
            s,
        )
    )

    story.append(P("Рецепт «боевого» шейка (по его описаниям)", s["h2"]))
    story.append(
        make_table(
            ["Ингредиент", "Заметка"],
            [
                ["Протеин (в т.ч. упоминал Muscle Milk)", "база белка"],
                ["Миндальное молоко", "жидкость"],
                ["Банан", "углеводы + калий"],
                ["Шпинат (несколько горстей)", "микронутриенты"],
                ["Арахисовая паста", "жиры + калории"],
                ["Авокадо / какао / овёс (варианты)", "плотность калорий"],
            ],
            [W * 0.55, W * 0.45],
            s,
        )
    )

    # Supplements
    story.append(P("5. Спортпит, витамины и минералы", s["h1"]))
    story.append(
        P(
            "После судорог («charlie horses everywhere») на подготовке к Reacher прошёл "
            "тесты. Ключевое трио, о котором говорил сам: <b>trace minerals, electrolytes, "
            "methylcobalamin B12</b>. Плюс протеин для набора 240+ г белка.",
            s["body"],
        )
    )
    story.append(
        make_table(
            ["Добавка", "Зачем (по его словам / обзорам)", "Детали"],
            [
                [
                    "Trace minerals (ConcenTrace)",
                    "судороги, минеральный дефицит",
                    "капли ежедневно; бренд, который называл",
                ],
                [
                    "Электролиты",
                    "гидратация, работа мышц",
                    "вместе с минералами, особенно в тренировочные дни",
                ],
                [
                    "Methylcobalamin (B12)",
                    "энергия, нервы; генетический дефицит",
                    "активная форма B12 после теста",
                ],
                [
                    "Whey / RTD протеин",
                    "добить белок и калории",
                    "шейки, Muscle Milk и др.",
                ],
                [
                    "Мультивитамин (в обзорах)",
                    "общий страховочный фон",
                    "вторичные источники",
                ],
                [
                    "BCAA / креатин (в обзорах)",
                    "восстановление / сила",
                    "не всегда подтверждено им лично",
                ],
            ],
            [W * 0.28, W * 0.36, W * 0.36],
            s,
        )
    )

    story.append(P("TRT (заместительная терапия тестостероном)", s["h2"]))
    story.append(
        P(
            "После 1 сезона анализы показали очень низкий тестостерон («no testosterone»). "
            "Врач назначил <b>медицинский TRT</b> перед 2 сезоном. Ричсон подчёркивает: "
            "это лечение дефицита, не «схема для зала». Самолечение гормонами опасно "
            "(сердце, фертильность, эндокринная система). Любые симптомы low-T — только "
            "к эндокринологу / урологу с анализами.",
            s["body"],
        )
    )
    story.append(
        P(
            "«There was a hormone that was missing for me, and I needed it.» — Alan Ritchson "
            "(Men's Health)",
            s["quote"],
        )
    )

    # Daily schedule
    story.append(P("6. Распорядок дня (реконструкция)", s["h1"]))
    story.append(
        P(
            "Точного публичного «часа по часам» нет; ниже — сборка из интервью о питании, "
            "тренировках, сауне и съёмочном режиме.",
            s["body"],
        )
    )
    story.append(
        make_table(
            ["Блок дня", "Что делает", "Комментарий"],
            [
                ["Утро", "Завтрак с белком + (часто) шейк", "ранний вклад в 4k+ ккал"],
                [
                    "Тренировка",
                    "20–30 мин силовой + кардио / HIIT",
                    "5 дней/нед.; не chase PR",
                ],
                [
                    "День",
                    "2–4 приёма пищи / перекусы",
                    "на съёмках — cook / ассистент по еде",
                ],
                [
                    "Экшен / бойка",
                    "fight choreography",
                    "отдельный кардио-стресс-тест",
                ],
                [
                    "Восстановление",
                    "сауна ≈ 15 мин («zen time»)",
                    "ментальная разгрузка + кровоток",
                ],
                ["Вечер", "плотный ужин ± десерт", "профицит без срыва к концу дня"],
                ["Ночь", "сон / отдых", "критично при высоком объёме"],
                ["Выходные", "rest / лёгкая активность", "поясница, суставы, ЦНС"],
            ],
            [W * 0.2, W * 0.38, W * 0.42],
            s,
        )
    )

    # Weekly overview
    story.append(P("7. Недельная карта", s["h1"]))
    story.append(
        make_table(
            ["День", "Силовая", "Кардио / прочее"],
            [
                ["Пн", "Грудь (Smith + кабели)", "HIIT ~20 мин"],
                ["Вт", "Спина + подтягивания", "бег"],
                ["Ср", "Ноги + пресс (без тяжёлых приседов)", "сани ~10 мин"],
                ["Чт", "Плечи + трапеции", "HIIT ~20 мин"],
                ["Пт", "Руки (суперсеты) + dips", "бег"],
                ["Сб", "Отдых / бойка / калистеника по самочувствию", "по ситуации"],
                ["Вс", "Отдых", "прогулка, растяжка"],
            ],
            [W * 0.12, W * 0.48, W * 0.4],
            s,
        )
    )

    # How to adapt
    story.append(P("8. Как адаптировать под себя (рекомендации)", s["h1"]))
    story.append(
        make_table(
            ["Уровень / цель", "Что менять"],
            [
                [
                    "Новичок",
                    "3 дня full-body или upper/lower; 8–15 повт.; калистеника-AMRAP 1–2×/нед.; белок 1.6–2.2 г/кг",
                ],
                [
                    "Средний (набор)",
                    "bro-split 4–5 дней; 12–20 повт. близко к отказу; профицит +250–500 ккал; трекинг веса 2–3 нед.",
                ],
                [
                    "Поддержание формы",
                    "короткие жёсткие сессии 4–5×; белок стабильно; 80/20; сауна/сон как часть плана",
                ],
                [
                    "Ограничения спины",
                    "как у него: lunges/split squat, тренажёры, без обязательных барбелл-squat/DL",
                ],
                [
                    "Здоровье",
                    "анализы (витамины, ферритин, B12, гормоны) до копирования добавок/TRT",
                ],
            ],
            [W * 0.28, W * 0.72],
            s,
        )
    )

    story.append(P("Практический чек-лист на 4 недели", s["h2"]))
    checklist = [
        "Зафиксировать текущий вес, обхваты груди/рук, фото раз в 2 недели.",
        "Выбрать сплит: либо Reacher bro-split, либо упрощённый 3–4 дня.",
        "Считать белок (цель: ≥1.8 г/кг) и калории; корректировать по весу.",
        "Добавить 1 калистеника-день (AMRAP 20–30 мин).",
        "Кардио 2–4×/нед. (HIIT или бег) + 1 «бойка»/интервалы.",
        "Сон 7–9 ч; после тяжёлых дней — сауна/горячий душ 10–15 мин.",
        "Добавки: начать с протеина + электролитов; B12/минералы — по анализам.",
        "Не копировать TRT «для размера» без диагноза.",
    ]
    for i, item in enumerate(checklist, 1):
        story.append(P(f"{i}. {item}", s["bullet"]))

    # Sources
    story.append(Spacer(1, 0.4 * cm))
    story.append(P("9. Источники", s["h1"]))
    sources = [
        "Men's Health — «Gym & Fridge» / Alan Ritchson diet & workout (фев. 2024)",
        "Men's Fitness — материалы о 3 ключевых добавках (minerals / electrolytes / B12)",
        "Generation Iron — Alan Ritchson Reacher Workout & Diet",
        "Set For Set — The Alan Ritchson Workout and Diet Plan",
        "FitnessVolt / Jacked Gorilla — сводные реконструкции программ (вторичные)",
        "Интервью о TRT после Season 1 (Men's Health и профильные обзоры)",
    ]
    for src in sources:
        story.append(P(f"• {src}", s["note"]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(
        P(
            "Составлено как практический справочник по публичным данным о системе "
            "Алана Ричсона. Сверяйте нагрузку с тренером и врачом.",
            s["footer"],
        )
    )

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
