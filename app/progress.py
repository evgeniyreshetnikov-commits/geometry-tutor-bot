from dataclasses import dataclass, asdict


@dataclass
class UserProgress:
    stars: int = 0
    effort: int = 0
    solved: int = 0
    quizzes: int = 0
    streak: int = 0


def ensure_progress(context):
    if "progress" not in context.user_data:
        context.user_data["progress"] = asdict(UserProgress())
    return context.user_data["progress"]


def add_stars(context, amount: int = 1):
    progress = ensure_progress(context)
    progress["stars"] += amount


def add_effort(context, amount: int = 1):
    progress = ensure_progress(context)
    progress["effort"] += amount


def add_solved(context, amount: int = 1):
    progress = ensure_progress(context)
    progress["solved"] += amount


def add_quiz(context, amount: int = 1):
    progress = ensure_progress(context)
    progress["quizzes"] += amount


def progress_text(context) -> str:
    progress = ensure_progress(context)
    return (
        "🌟 Мой прогресс\n\n"
        f"Звёзды: {progress['stars']}\n"
        f"Старание: {progress['effort']}\n"
        f"Решённых заданий: {progress['solved']}\n"
        f"Викторин пройдено: {progress['quizzes']}\n\n"
        "Ты молодец, когда стараешься и пробуешь сам, даже если ошибаешься."
    )
