from telegram import Update
from telegram.ext import ContextTypes

from .keyboards import (
    persistent_keyboard,
    main_menu_keyboard,
    topics_inline_keyboard,
    after_action_inline_keyboard,
    quiz_inline_keyboard,
)
from .quiz import QUIZ_TEXTS, TOPIC_TEXTS
from .progress import ensure_progress, add_stars, add_effort, add_solved, add_quiz, progress_text


WELCOME_TEXT = (
    "Привет! Я твой помощник по геометрии за 7 класс 🙂\n\n"
    "Я объясняю тему простыми словами, помогаю решать по шагам, "
    "даю тренировку и мини-викторины.\n"
    "Я не даю готовые ответы, зато помогаю понять, как дойти до решения самому.\n\n"
    "Нажми на кнопку ниже."
)

MAIN_MENU_TEXT = (
    "Главное меню\n\n"
    "Выбери, чем хочешь заняться 👇"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ensure_progress(context)
    await update.message.reply_text(WELCOME_TEXT, reply_markup=persistent_keyboard())
    await update.message.reply_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())


async def explain_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Выбери тему. Я объясню её просто и коротко, а потом дам маленькое задание 👇",
        reply_markup=topics_inline_keyboard(),
    )


async def solve_step_by_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Пришли условие задачи текстом или фото.\n\n"
        "Я не дам готовый ответ, но помогу решить по шагам: "
        "сначала разберём, что известно, потом выберем нужное свойство.",
        reply_markup=after_action_inline_keyboard(),
    )


async def training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Тренировка 🏋️\n\n"
        "Вот короткое задание:\n"
        "Один из смежных углов равен 70°.\n"
        "Как ты думаешь, чему равен второй?\n\n"
        "Не спеши. Сначала вспомни: чему равна сумма смежных углов?",
        reply_markup=after_action_inline_keyboard(),
    )


async def mini_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Мини-викторина 🎯\n\nВыбери тему викторины:",
        reply_markup=quiz_inline_keyboard(),
    )


async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(progress_text(context), reply_markup=after_action_inline_keyboard())


async def parents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "👨‍👩‍👧 Для родителей\n\n"
        "Бот не выдаёт готовые ответы и не решает домашнюю работу за ребёнка.\n"
        "Он объясняет тему простым языком, задаёт наводящие вопросы, "
        "проверяет шаги решения и поддерживает мотивацию.\n\n"
        "На этом этапе поддерживаются текст и фото."
    )
    await update.message.reply_text(text, reply_markup=after_action_inline_keyboard())


async def send_file_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Пришли фото задачи или текст условия.\n\n"
        "Следующим этапом можно добавить полноценную поддержку PDF, DOCX, JPG и PNG.",
        reply_markup=after_action_inline_keyboard(),
    )


async def check_my_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Напиши свой шаг или пришли фото решения.\n\n"
        "Я скажу, что у тебя уже получилось хорошо, "
        "и помогу найти место, которое стоит проверить.",
        reply_markup=after_action_inline_keyboard(),
    )


async def hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_effort(context)
    await update.message.reply_text(
        "Подсказка 💛\n\n"
        "Сначала не ищи ответ сразу.\n"
        "Попробуй определить:\n"
        "1) что известно,\n"
        "2) что нужно найти,\n"
        "3) какое свойство здесь подходит.\n\n"
        "Можешь прислать условие, и мы разберём его вместе.",
        reply_markup=after_action_inline_keyboard(),
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in TOPIC_TEXTS:
        add_stars(context)
        await query.message.reply_text(TOPIC_TEXTS[data], reply_markup=after_action_inline_keyboard())
        return

    if data in QUIZ_TEXTS:
        add_quiz(context)
        await query.message.reply_text(QUIZ_TEXTS[data], reply_markup=after_action_inline_keyboard())
        return

    if data == "help_hint":
        add_effort(context)
        await query.message.reply_text(
            "Подсказка 🔍\n\n"
            "Посмотри не на ответ, а на правило.\n"
            "Какая теорема или свойство подходит здесь лучше всего?",
            reply_markup=after_action_inline_keyboard(),
        )
        return

    if data == "next_step":
        await query.message.reply_text(
            "Следующий шаг ➡️\n\n"
            "Сначала выпиши, что известно в условии.\n"
            "Потом напиши, что нужно найти.\n"
            "После этого выберем подходящее свойство.",
            reply_markup=after_action_inline_keyboard(),
        )
        return

    if data == "more_task":
        add_solved(context)
        add_stars(context)
        await query.message.reply_text(
            "🎯 Ещё задача\n\n"
            "Один из вертикальных углов равен 40°.\n"
            "Не пиши сразу ответ.\n"
            "Сначала вспомни: что можно сказать о вертикальных углах?",
            reply_markup=after_action_inline_keyboard(),
        )
        return

    if data == "go_menu":
        await query.message.reply_text(MAIN_MENU_TEXT, reply_markup=main_menu_keyboard())
        return


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_effort(context)
    await update.message.reply_text(
        "Файл получил 📎\n\n"
        "В этой версии бот принимает файл, но ещё не разбирает его содержимое автоматически.\n"
        "Для полной поддержки PDF/DOCX/JPG можно сделать следующий этап.",
        reply_markup=after_action_inline_keyboard(),
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_effort(context)
    await update.message.reply_text(
        "Фото получил 🖼️\n\n"
        "Давай начнём с разбора условия.\n"
        "Что известно в задаче и что нужно найти?",
        reply_markup=after_action_inline_keyboard(),
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()

    routes = {
        "🏠 Главное меню": show_main_menu,
        "📘 Объясни тему": explain_topic,
        "🧠 Решим по шагам": solve_step_by_step,
        "🏋️ Тренировка": training,
        "🎯 Мини-викторина": mini_quiz,
        "🌟 Мой прогресс": progress,
        "👨‍👩‍👧 Для родителей": parents,
        "📎 Отправить файл": send_file_info,
        "✏️ Проверить мой шаг": check_my_step,
        "💛 Подсказка": hint,
    }

    if text in routes:
        await routes[text](update, context)
        return

    lowered = text.lower()
    forbidden_patterns = [
        "дай ответ",
        "реши полностью",
        "напиши только ответ",
        "просто ответ",
        "без объяснений",
    ]

    if any(pattern in lowered for pattern in forbidden_patterns):
        add_effort(context)
        await update.message.reply_text(
            "Готовый ответ я не дам, но помогу быстро разобраться.\n\n"
            "Давай начнём с первого шага: что известно в условии?",
            reply_markup=after_action_inline_keyboard(),
        )
        return

    await update.message.reply_text(
        "Давай разберёмся вместе.\n\n"
        "Напиши условие задачи или выбери кнопку:\n"
        "• 📘 Объясни тему\n"
        "• 🧠 Решим по шагам\n"
        "• ✏️ Проверить мой шаг",
        reply_markup=main_menu_keyboard(),
    )
