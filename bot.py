import io
import os
import re
import html
import random
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from telegram import (
    Update,
    Document,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

try:
    import fitz
except Exception:
    fitz = None

try:
    from docx import Document as DocxDocument
except Exception:
    DocxDocument = None

try:
    from PIL import Image, ImageOps, ImageFilter
except Exception:
    Image = None
    ImageOps = None
    ImageFilter = None

try:
    import pytesseract
except Exception:
    pytesseract = None

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

MAIN_REPLY_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("📎 Отправить файл")],
        [KeyboardButton("📝 Проверить шаг"), KeyboardButton("🌟 Поддержка")],
    ],
    resize_keyboard=True,
)

PRAISES = [
    "Хороший ход 🌟",
    "Отличная мысль 👍",
    "Ты уже близко ⭐",
    "Сильный шаг 💛",
]
ENCOURAGEMENTS = [
    "В геометрии идея не всегда видна сразу 🙂",
    "Давай найдём один маленький факт и пойдём дальше 💛",
    "Не спеши — здесь важнее заметить связь 🌈",
]
PROVOCATION_PATTERNS = [
    r"готовое решение", r"просто ответ", r"дай ответ", r"без объяснений",
    r"докажи за меня", r"реши за меня", r"сделай за меня", r"мне срочно",
    r"только ответ", r"не объясняй", r"скажи правильное доказательство",
]

TOPIC_HINTS = {
    "угол": ("Угол образуют два луча с общей вершиной.", ["Какая вершина у угла?", "Какие два луча его образуют?"], "Назови вершину и стороны угла."),
    "смеж": ("Смежные углы вместе дают 180°.", ["Эти углы имеют общую сторону?", "Остальные стороны образуют прямую?"], "Запиши равенство для суммы этих углов."),
    "вертик": ("Вертикальные углы равны.", ["Какие углы расположены напротив друг друга?", "Какое свойство можно применить?"], "Найди пару вертикальных углов и запиши, что они равны."),
    "треуг": ("В треугольнике важно смотреть на стороны, углы и признаки равенства.", ["Что известно про стороны и углы?", "Есть ли здесь признак равенства треугольников?"], "Выпиши всё известное о треугольнике коротким списком."),
    "равенств": ("Для равенства треугольников нужен подходящий признак.", ["Есть ли две стороны и угол между ними?", "Или сторона и два прилежащих угла?"], "Определи, какой признак здесь подходит."),
    "медиан": ("Медиана идёт из вершины к середине противоположной стороны.", ["Какая точка — середина стороны?", "Из какой вершины проведён отрезок?"], "Назови сторону и её середину."),
    "биссект": ("Биссектриса делит угол на два равных угла.", ["Какой угол делят пополам?", "Какие два угла при этом равны?"], "Запиши пару равных углов."),
    "высот": ("Высота перпендикулярна стороне или её продолжению.", ["Из какой вершины она проведена?", "К какой стороне она перпендикулярна?"], "Запиши, какие прямые перпендикулярны."),
    "паралл": ("При параллельных прямых полезно искать накрест лежащие и соответственные углы.", ["Какие прямые параллельны?", "Есть ли секущая?"], "Найди одну пару углов, связь между которыми можно использовать."),
}

TOPICS_MENU_TEXT = (
    "📐 Темы геометрии 7 класса:\n\n"
    "• углы, смежные и вертикальные углы\n"
    "• треугольник и его элементы\n"
    "• признаки равенства треугольников\n"
    "• медиана, биссектриса, высота\n"
    "• свойства равнобедренного треугольника\n"
    "• параллельные прямые и секущая\n"
    "• доказательства\n\n"
    "Выбери режим ниже или пришли своё задание."
)

BADGES = {
    "first_star": "🌟 Первый луч",
    "angles_master": "📐 Знаток углов",
    "triangles_master": "🔺 Мастер треугольников",
    "quiz_3": "🧠 Любитель викторин",
    "training_5": "🏋️ Упорный геометр",
    "streak_5": "🔥 Серия 5",
}

DAILY_TASKS = [
    {"question": "Вертикальные углы равны? Ответь: да или нет.", "answer": "да", "hint": "Подумай про углы, которые лежат друг напротив друга."},
    {"question": "Чему равна сумма смежных углов? Напиши только число.", "answer": "180", "hint": "Они образуют развёрнутый угол."},
    {"question": "Что делит угол на две равные части: медиана, биссектриса или высота?", "answer": "биссектриса", "hint": "В самом слове спрятано «делит»."},
    {"question": "Как называется отрезок из вершины к середине противоположной стороны?", "answer": "медиана", "hint": "Ключевое слово — середина."},
]
IDEA_PROMPTS = [
    "Какие фигуры или углы ты уже видишь на рисунке?",
    "Что в условии уже дано: равные стороны, равные углы, параллельные прямые?",
    "Какой первый факт можно записать без вычислений?",
    "Какое свойство может сработать здесь первым?",
]

@dataclass
class ExampleTask:
    text: str
    answer: str
    hint1: str
    hint2: str
    hint3: str
    topic: str


def main_inline_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 Объясни тему", callback_data="menu_topic"), InlineKeyboardButton("💡 Найти идею", callback_data="idea_mode")],
        [InlineKeyboardButton("🧠 Разберём доказательство", callback_data="menu_steps"), InlineKeyboardButton("🧩 Шаблон доказательства", callback_data="proof_template")],
        [InlineKeyboardButton("🏋️ Тренировка", callback_data="train_start"), InlineKeyboardButton("🎯 Мини-викторина", callback_data="quiz_start")],
        [InlineKeyboardButton("📅 Задание дня", callback_data="daily_task"), InlineKeyboardButton("🌟 Мой прогресс", callback_data="show_progress")],
        [InlineKeyboardButton("🏅 Достижения", callback_data="show_badges"), InlineKeyboardButton("👨‍👩‍👧 Для родителей", callback_data="parents_info")],
    ])


def build_progress_bar(stars: int) -> str:
    filled = min(stars // 5, 10)
    return "★" * filled + "☆" * (10 - filled)


def default_stats() -> dict:
    return {"stars": 0, "level": 1, "solved_training": 0, "quiz_correct": 0, "streak": 0, "badges": [], "last_daily_date": ""}


def get_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> dict:
    if "stats" not in context.user_data:
        context.user_data["stats"] = default_stats()
    return context.user_data["stats"]


def add_stars(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int) -> dict:
    stats = get_user_stats(update, context)
    stats["stars"] += amount
    stats["level"] = max(1, stats["stars"] // 10 + 1)
    return stats


def grant_badges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> list[str]:
    stats = get_user_stats(update, context)
    badges = set(stats.get("badges", []))
    new_badges = []
    rules = [
        ("first_star", stats["stars"] >= 1),
        ("angles_master", stats["quiz_correct"] >= 3),
        ("triangles_master", stats["stars"] >= 15),
        ("quiz_3", stats["quiz_correct"] >= 3),
        ("training_5", stats["solved_training"] >= 5),
        ("streak_5", stats["streak"] >= 5),
    ]
    for key, ok in rules:
        if ok and key not in badges:
            badges.add(key)
            new_badges.append(BADGES[key])
    if new_badges:
        stats["badges"] = sorted(badges)
    return new_badges


def format_badges(stats: dict) -> str:
    badge_keys = stats.get("badges", [])
    if not badge_keys:
        return "🏅 Пока достижений ещё нет. Но первое уже близко!"
    return "🏅 Твои достижения\n\n" + "\n".join(f"• {BADGES.get(key, key)}" for key in badge_keys)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def looks_like_provocation(text: str) -> bool:
    lowered = normalize_text(text)
    return any(re.search(pattern, lowered) for pattern in PROVOCATION_PATTERNS)


def detect_topic_pack(text: str):
    lowered = normalize_text(text)
    for key, pack in TOPIC_HINTS.items():
        if key in lowered:
            return pack
    return None


def truncate_text(text: str, max_len: int = 3500) -> str:
    text = text.strip()
    return text if len(text) <= max_len else text[:max_len] + "\n\n[Текст сокращён]"


def random_praise() -> str:
    return random.choice(PRAISES)


def random_encouragement() -> str:
    return random.choice(ENCOURAGEMENTS)


def maybe_badge_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    new_badges = grant_badges(update, context)
    return "" if not new_badges else "\n\n🎉 Новое достижение:\n" + "\n".join(f"• {name}" for name in new_badges)


def build_provocation_reply() -> str:
    return "Я не дам готовое решение, но помогу тебе самому его построить 🙂\n\nСначала найдём: что дано, что нужно доказать и какой первый факт можно записать."


def build_tutor_reply(user_text: str) -> str:
    cleaned = user_text.strip()
    lowered = normalize_text(cleaned)
    quick = {
        "🏠 главное меню": "Выбери режим ниже 👇",
        "📎 отправить файл": "Чтобы отправить файл, нажми на скрепку рядом с полем ввода и выбери PDF, DOCX, JPG или PNG.",
        "📝 проверить шаг": "Пришли один свой шаг. Я проверю логику и подскажу только следующий шаг.",
        "🌟 поддержка": random_encouragement(),
    }
    if lowered in quick:
        return quick[lowered]
    if looks_like_provocation(cleaned):
        return build_provocation_reply()
    if len(cleaned) < 6:
        return "Пришли задачу текстом или фото. Сначала найдём первый полезный факт."
    topic_pack = detect_topic_pack(cleaned)
    if topic_pack:
        explanation, questions, next_step = topic_pack
        return f"{explanation}\n\n1) {questions[0]}\n2) {questions[1]}\n\nСледующий шаг: {next_step}"
    if any(word in lowered for word in ["мой шаг", "я доказал", "я думаю", "получилось", "мой вывод"]):
        return "Проверим один шаг:\n1) Он опирается на условие или свойство?\n2) Здесь нет пропуска в рассуждении?\n3) Что из этого следует дальше?"
    return "Давай начнём просто:\n1) Что дано?\n2) Что нужно доказать или найти?\n3) Какой первый факт можно записать?"


def generate_training_tasks() -> list[ExampleTask]:
    variants = [
        ExampleTask("Как называются углы, которые лежат друг напротив друга при пересечении двух прямых?", "вертикальные", "Посмотри на углы напротив друг друга.", "Они не рядом, а строго друг против друга.", "Это углы, про которые говорят: они равны и стоят напротив.", "углы"),
        ExampleTask("Чему равна сумма смежных углов?", "180", "Они образуют развёрнутый угол.", "Развёрнутый угол — это половина полного круга.", "Запиши число градусов в развёрнутом угле.", "смежные углы"),
        ExampleTask("Что делит угол на две равные части?", "биссектриса", "Подумай, какой отрезок делит угол пополам.", "Он начинается в вершине угла.", "Его название часто встречается в задачах на равные углы.", "биссектриса"),
        ExampleTask("Как называется отрезок из вершины к середине противоположной стороны?", "медиана", "Ключевое слово — середина.", "Этот отрезок идёт из вершины треугольника.", "Он соединяет вершину с серединой стороны.", "медиана"),
        ExampleTask("Как называется отрезок, проведённый из вершины перпендикулярно стороне?", "высота", "Он образует прямой угол.", "Его главный признак — перпендикулярность.", "Этот отрезок проводят из вершины к стороне под 90°.", "высота"),
        ExampleTask("Сколько градусов в прямом угле?", "90", "Это четверть полного оборота.", "Полный угол — 360°.", "Раздели полный угол на 4.", "угол"),
    ]
    return random.sample(variants, 5)


def generate_quiz_question() -> dict:
    variants = [
        {"question": "Что верно для вертикальных углов?", "answer": "они равны", "hint": "Подумай про углы, которые лежат друг напротив друга.", "explain": "Вертикальные углы равны."},
        {"question": "Что верно для смежных углов?", "answer": "их сумма 180", "hint": "Они образуют развёрнутый угол.", "explain": "Смежные углы дают 180°."},
        {"question": "Что делает биссектриса?", "answer": "делит угол пополам", "hint": "Она работает именно с углом.", "explain": "Биссектриса делит угол на два равных угла."},
        {"question": "Что такое медиана?", "answer": "отрезок к середине стороны", "hint": "Ключевое слово — середина.", "explain": "Медиана идёт к середине противоположной стороны."},
    ]
    return random.choice(variants)


def format_progress_text(stats: dict) -> str:
    return (
        "🌟 Твой прогресс\n\n"
        f"Уровень: <b>{stats['level']}</b>\n"
        f"Звёздочки: <b>{stats['stars']}</b>\n"
        f"Тренировок: <b>{stats['solved_training']}</b>\n"
        f"Викторин верно: <b>{stats['quiz_correct']}</b>\n"
        f"Серия: <b>{stats['streak']}</b>\n\n"
        f"Прогресс: <code>{build_progress_bar(stats['stars'])}</code>"
    )


def daily_task_for_today() -> dict:
    idx = datetime.now(timezone.utc).timetuple().tm_yday % len(DAILY_TASKS)
    return DAILY_TASKS[idx]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    if fitz is None:
        return "Не удалось прочитать PDF: библиотека PyMuPDF не установлена."
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc).strip() or "В PDF не найден текст. Возможно, это скан."
    except Exception as exc:
        logger.exception("PDF parse error: %s", exc)
        return "Не удалось прочитать PDF-файл."


def extract_text_from_docx(file_bytes: bytes) -> str:
    if DocxDocument is None:
        return "Не удалось прочитать Word-файл: библиотека python-docx не установлена."
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()) or "В Word-файле не найден текст."
    except Exception as exc:
        logger.exception("DOCX parse error: %s", exc)
        return "Не удалось прочитать Word-файл."


def image_variants(image):
    yield image
    if ImageOps is not None:
        gray = ImageOps.grayscale(image)
        yield gray
        yield ImageOps.autocontrast(gray)
        enlarged = ImageOps.autocontrast(gray).resize((gray.width * 2, gray.height * 2))
        yield enlarged
        if ImageFilter is not None:
            yield enlarged.filter(ImageFilter.SHARPEN)


def ocr_quality_good(text: str) -> bool:
    text = text.strip()
    if len(text) < 18:
        return False
    cyr = len(re.findall(r"[А-Яа-яЁё]", text))
    digits = len(re.findall(r"\d", text))
    letters = len(re.findall(r"[A-Za-zА-Яа-яЁё]", text))
    bad = len(re.findall(r"[^\w\s.,:;!?%°=+\-()/]", text))
    return (cyr + digits >= 10) and letters >= 8 and bad < max(6, len(text) // 8)


def extract_text_from_image(file_bytes: bytes) -> str:
    if Image is None or pytesseract is None:
        return "OCR_NOT_AVAILABLE"
    try:
        image = Image.open(io.BytesIO(file_bytes))
        candidates = []
        for variant in image_variants(image):
            for config in ["--psm 6", "--psm 11", "--psm 4"]:
                try:
                    text = pytesseract.image_to_string(variant, lang="rus+eng", config=config).strip()
                except Exception:
                    continue
                if text:
                    candidates.append(text)
                    if ocr_quality_good(text):
                        return text
        if candidates:
            best = max(candidates, key=len)
            return best if ocr_quality_good(best) else "OCR_LOW_QUALITY"
        return "OCR_LOW_QUALITY"
    except Exception as exc:
        logger.exception("Image OCR error: %s", exc)
        return "OCR_LOW_QUALITY"


async def send_main_menu(target, text: str, edit: bool = False):
    if edit:
        await target.edit_message_text(text, reply_markup=main_inline_menu(), parse_mode="HTML")
    else:
        await target.reply_text(text, reply_markup=main_inline_menu(), parse_mode="HTML")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    get_user_stats(update, context)
    await update.message.reply_text(
        "Привет! Я помощник по геометрии 7 класса v5 🙂\nПомогаю понять идею, разобрать доказательство и потренироваться без готовых решений.",
        reply_markup=MAIN_REPLY_MENU,
    )
    await send_main_menu(update.message, "<b>Главное меню</b>\n\nВыбери режим 👇")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Как со мной работать:\n\n• пришли задачу текстом или файлом\n• выбери режим\n• получай подсказки по шагам\n• собирай звёздочки и достижения",
        reply_markup=MAIN_REPLY_MENU,
    )


async def topics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_main_menu(update.message, TOPICS_MENU_TEXT)


async def parents_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Для родителей:\n\nБот не выдаёт готовые доказательства. Он учит ребёнка видеть идею, замечать свойства и строить рассуждение по шагам.",
        reply_markup=MAIN_REPLY_MENU,
    )


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(format_progress_text(get_user_stats(update, context)), parse_mode="HTML")


async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    task = daily_task_for_today()
    context.user_data["mode"] = "daily"
    context.user_data["daily_task"] = task
    await update.message.reply_text(f"📅 Задание дня\n\n{task['question']}\n\nЕсли трудно, напиши: подсказка", reply_markup=MAIN_REPLY_MENU)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    stats = get_user_stats(update, context)
    if data == "menu_topic":
        await send_main_menu(query, TOPICS_MENU_TEXT, edit=True)
        return
    if data == "idea_mode":
        context.user_data["mode"] = "idea"
        await send_main_menu(query, "<b>Найти идею</b>\n\nПришли задачу или рисунок. Я помогу найти первый полезный факт.", edit=True)
        return
    if data == "menu_steps":
        context.user_data["mode"] = "proof"
        await send_main_menu(query, "<b>Разберём доказательство</b>\n\nПришли задачу. Мы пройдём: дано → что доказать → первый факт → следующий вывод.", edit=True)
        return
    if data == "proof_template":
        await send_main_menu(query, "<b>Шаблон доказательства</b>\n\n1) Дано\n2) Нужно доказать\n3) Полезные факты\n4) Свойство или признак\n5) Вывод\n\nНапиши задачу, и мы заполним шаблон вместе.", edit=True)
        return
    if data == "show_progress":
        await send_main_menu(query, format_progress_text(stats), edit=True)
        return
    if data == "show_badges":
        await send_main_menu(query, format_badges(stats), edit=True)
        return
    if data == "parents_info":
        await send_main_menu(query, "<b>Для родителей</b>\n\nБот не решает за ребёнка. Он тренирует ход мысли, внимание к чертежу и умение строить доказательство.", edit=True)
        return
    if data == "daily_task":
        task = daily_task_for_today()
        context.user_data["mode"] = "daily"
        context.user_data["daily_task"] = task
        await send_main_menu(query, f"<b>Задание дня</b>\n\n{html.escape(task['question'])}\n\nЕсли трудно, напиши <code>подсказка</code>.", edit=True)
        return
    if data == "train_start":
        tasks = generate_training_tasks()
        context.user_data["training_tasks"] = tasks
        context.user_data["training_index"] = 0
        context.user_data["training_hint_level"] = 0
        context.user_data["mode"] = "training"
        first = tasks[0]
        await send_main_menu(query, f"<b>Тренировка из 5 заданий</b>\n\nЗадание 1 из 5\n{html.escape(first.text)}\n\nНапиши короткий ответ или слово <code>подсказка</code>.", edit=True)
        return
    if data == "quiz_start":
        q = generate_quiz_question()
        context.user_data["mode"] = "quiz"
        context.user_data["quiz_question"] = q
        await send_main_menu(query, f"<b>Мини-викторина</b>\n\n{html.escape(q['question'])}\n\nНапиши ответ сам(а).", edit=True)
        return


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = (update.message.text or "").strip()
    stats = get_user_stats(update, context)
    lowered = normalize_text(user_text)
    if lowered == "🏠 главное меню":
        await send_main_menu(update.message, "<b>Главное меню</b>\n\nВыбери режим 👇")
        return
    mode = context.user_data.get("mode")
    if mode == "daily":
        task = context.user_data.get("daily_task", daily_task_for_today())
        if lowered == "подсказка":
            await update.message.reply_text(f"Подсказка 💡 {task['hint']}", reply_markup=MAIN_REPLY_MENU)
            return
        if lowered == normalize_text(task["answer"]):
            today = datetime.now(timezone.utc).date().isoformat()
            if stats.get("last_daily_date") != today:
                stats["last_daily_date"] = today
                stats["streak"] += 1
                add_stars(update, context, 2)
            await update.message.reply_text(f"{random_praise()}\n\nЗадание дня выполнено! +2 ⭐{maybe_badge_text(update, context)}", reply_markup=MAIN_REPLY_MENU)
        else:
            stats["streak"] = 0
            await update.message.reply_text(f"Пока неверно. {task['hint']}", reply_markup=MAIN_REPLY_MENU)
        context.user_data["mode"] = None
        return
    if mode == "training":
        tasks = context.user_data.get("training_tasks", [])
        idx = context.user_data.get("training_index", 0)
        if idx < len(tasks):
            task = tasks[idx]
            if lowered == "подсказка":
                hint_level = context.user_data.get("training_hint_level", 0) + 1
                context.user_data["training_hint_level"] = min(hint_level, 3)
                hint_text = {1: task.hint1, 2: task.hint2, 3: task.hint3}[min(hint_level, 3)]
                await update.message.reply_text(f"Подсказка {min(hint_level,3)} 💡\n\n{hint_text}", reply_markup=MAIN_REPLY_MENU)
                return
            if lowered == normalize_text(task.answer):
                stats["solved_training"] += 1
                stats["streak"] += 1
                context.user_data["training_index"] = idx + 1
                context.user_data["training_hint_level"] = 0
                add_stars(update, context, 1)
                if idx + 1 >= len(tasks):
                    add_stars(update, context, 3)
                    context.user_data["mode"] = None
                    await update.message.reply_text(f"🎉 Тренировка завершена!\n\nТы выполнил(а) 5 из 5 заданий.\n+3 дополнительные ⭐{maybe_badge_text(update, context)}", reply_markup=MAIN_REPLY_MENU)
                    return
                next_task = tasks[idx + 1]
                await update.message.reply_text(f"{random_praise()}\n\n+1 ⭐\nСледующее задание:\n{next_task.text}", reply_markup=MAIN_REPLY_MENU)
                return
            stats["streak"] = 0
            await update.message.reply_text(f"{random_encouragement()}\n\nПопробуй ещё раз или напиши: подсказка", reply_markup=MAIN_REPLY_MENU)
            return
    if mode == "quiz":
        q = context.user_data.get("quiz_question")
        if not q:
            await update.message.reply_text("Викторина уже закончилась. Выбери новую задачу в меню 🙂", reply_markup=MAIN_REPLY_MENU)
            return
        if lowered == "подсказка":
            await update.message.reply_text(f"Подсказка 💡 {q['hint']}", reply_markup=MAIN_REPLY_MENU)
            return
        accepted = {normalize_text(q["answer"]) }
        if q["answer"] == "они равны":
            accepted.update(["равны", "они равны"])
        if q["answer"] == "их сумма 180":
            accepted.update(["180", "сумма 180", "их сумма 180", "180 градусов"])
        if q["answer"] == "делит угол пополам":
            accepted.update(["делит угол на две равные части", "пополам"])
        if q["answer"] == "отрезок к середине стороны":
            accepted.update(["к середине противоположной стороны", "отрезок к середине противоположной стороны"])
        if lowered in accepted:
            stats["quiz_correct"] += 1
            stats["streak"] += 1
            add_stars(update, context, 2)
            await update.message.reply_text(f"✅ Верно!\n\n{q['explain']}\n\n+2 ⭐{maybe_badge_text(update, context)}", reply_markup=MAIN_REPLY_MENU)
            context.user_data["mode"] = None
            context.user_data.pop("quiz_question", None)
            return
        stats["streak"] = 0
        await update.message.reply_text(f"❌ Пока неверно.\n\nПодсказка: {q['hint']}\n\nПопробуй ещё раз.", reply_markup=MAIN_REPLY_MENU)
        return
    if mode == "idea":
        await update.message.reply_text("💡 Идея задачи\n\n" + random.choice(IDEA_PROMPTS), reply_markup=MAIN_REPLY_MENU)
        return
    await update.message.reply_text(build_tutor_reply(user_text), reply_markup=MAIN_REPLY_MENU)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document: Document = update.message.document
    file_name = (document.file_name or "").lower()
    telegram_file = await context.bot.get_file(document.file_id)
    file_bytes = await telegram_file.download_as_bytearray()
    if file_name.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(bytes(file_bytes))
    elif file_name.endswith(".docx"):
        extracted_text = extract_text_from_docx(bytes(file_bytes))
    elif any(file_name.endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
        extracted_text = extract_text_from_image(bytes(file_bytes))
        if extracted_text in {"OCR_NOT_AVAILABLE", "OCR_LOW_QUALITY"}:
            await update.message.reply_text(
                "Я получил изображение как файл, но не смог хорошо распознать текст.\n\n"
                "Попробуй так:\n"
                "1) обрежь только одну задачу\n"
                "2) выбери светлый фон и тёмный текст\n"
                "3) пришли PDF или напиши условие текстом\n"
                "4) проверь OCR в Railway: RAILPACK_DEPLOY_APT_PACKAGES = tesseract-ocr tesseract-ocr-rus",
                reply_markup=MAIN_REPLY_MENU,
            )
            return
    else:
        await update.message.reply_text("Я поддерживаю PDF, DOCX, JPG и PNG.", reply_markup=MAIN_REPLY_MENU)
        return
    extracted_text = truncate_text(extracted_text)
    await update.message.reply_text(f"Я посмотрел файл 🙂\n\nВот что удалось прочитать:\n\n{extracted_text}\n\nТеперь скажи: что дано и что нужно доказать?", reply_markup=MAIN_REPLY_MENU)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]
    telegram_file = await context.bot.get_file(photo.file_id)
    file_bytes = await telegram_file.download_as_bytearray()
    extracted_text = extract_text_from_image(bytes(file_bytes))
    if extracted_text == "OCR_NOT_AVAILABLE":
        await update.message.reply_text(
            "Я получил фото, но OCR сейчас недоступен.\n\n"
            "Проверь, установлен ли OCR на Railway:\n"
            "RAILPACK_DEPLOY_APT_PACKAGES = tesseract-ocr tesseract-ocr-rus",
            reply_markup=MAIN_REPLY_MENU,
        )
        return
    if extracted_text == "OCR_LOW_QUALITY":
        await update.message.reply_text(
            "Я увидел чертёж, но текст на фото распознался плохо.\n\n"
            "Попробуй так:\n"
            "1) обрежь только одну задачу\n"
            "2) сделай фото ровно сверху\n"
            "3) выбери светлый фон и тёмный текст\n"
            "4) пришли скриншот, PDF или текст условия\n\n"
            "Если хочешь, можешь сразу написать: где прямой угол, какой угол дан и что нужно найти.",
            reply_markup=MAIN_REPLY_MENU,
        )
        return
    extracted_text = truncate_text(extracted_text)
    await update.message.reply_text(
        f"Я посмотрел фото 🙂\n\nВот что удалось распознать:\n\n{extracted_text}\n\nТеперь скажи: что дано и что нужно найти или доказать?",
        reply_markup=MAIN_REPLY_MENU,
    )


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Я могу помочь с задачей, идеей, доказательством, тренировкой или файлом 🙂", reply_markup=MAIN_REPLY_MENU)



def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("Set BOT_TOKEN in Railway Variables.")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("topics", topics_command))
    application.add_handler(CommandHandler("parents", parents_command))
    application.add_handler(CommandHandler("progress", progress_command))
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.ALL, fallback))
    logger.info("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
