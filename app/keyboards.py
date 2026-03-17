from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def persistent_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("📎 Отправить файл")],
        [KeyboardButton("✏️ Проверить мой шаг"), KeyboardButton("💛 Подсказка")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Напиши сообщение или выбери кнопку",
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("📘 Объясни тему"), KeyboardButton("🧠 Решим по шагам")],
        [KeyboardButton("🏋️ Тренировка"), KeyboardButton("🎯 Мини-викторина")],
        [KeyboardButton("🌟 Мой прогресс"), KeyboardButton("👨‍👩‍👧 Для родителей")],
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("📎 Отправить файл")],
        [KeyboardButton("✏️ Проверить мой шаг"), KeyboardButton("💛 Подсказка")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выбери, чем хочешь заняться 👇",
    )


def topics_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📐 Углы", callback_data="topic_angles"),
            InlineKeyboardButton("📏 Отрезок и луч", callback_data="topic_segment_ray"),
        ],
        [
            InlineKeyboardButton("🔺 Треугольники", callback_data="topic_triangles"),
            InlineKeyboardButton("🟰 Равенство треугольников", callback_data="topic_congruence"),
        ],
        [
            InlineKeyboardButton("📎 Смежные углы", callback_data="topic_adjacent"),
            InlineKeyboardButton("🔄 Вертикальные углы", callback_data="topic_vertical"),
        ],
        [InlineKeyboardButton("🏠 В меню", callback_data="go_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def after_action_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🔍 Подсказка", callback_data="help_hint"),
            InlineKeyboardButton("➡️ Следующий шаг", callback_data="next_step"),
        ],
        [
            InlineKeyboardButton("🎯 Ещё задача", callback_data="more_task"),
            InlineKeyboardButton("🏠 В меню", callback_data="go_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def quiz_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📐 По углам", callback_data="quiz_angles"),
            InlineKeyboardButton("🔺 По треугольникам", callback_data="quiz_triangles"),
        ],
        [
            InlineKeyboardButton("📎 Смешанная", callback_data="quiz_mixed"),
            InlineKeyboardButton("🏠 В меню", callback_data="go_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
