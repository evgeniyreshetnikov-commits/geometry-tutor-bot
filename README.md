# Geometry Tutor Bot

Telegram-бот по геометрии для 7 класса.

Бот:
- объясняет тему простыми словами
- помогает решать по шагам
- не даёт готовые ответы
- поддерживает тренировку, мини-викторины, прогресс и блок для родителей

## Структура

```text
geometry-tutor-bot/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ handlers.py
│  ├─ keyboards.py
│  ├─ prompts.py
│  ├─ quiz.py
│  └─ progress.py
├─ requirements.txt
├─ Procfile
├─ railway.toml
├─ .env.example
├─ .gitignore
└─ README.md
```

## Локальный запуск

### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:TELEGRAM_BOT_TOKEN="your_token"
python -m app.main
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="your_token"
python -m app.main
```

## Команды / кнопки

Главное меню:
- 📘 Объясни тему
- 🧠 Решим по шагам
- 🏋️ Тренировка
- 🎯 Мини-викторина
- 🌟 Мой прогресс
- 👨‍👩‍👧 Для родителей

Постоянная клавиатура:
- 🏠 Главное меню
- 📎 Отправить файл
- ✏️ Проверить мой шаг
- 💛 Подсказка

## Деплой на GitHub

1. Создай новый репозиторий на GitHub.
2. Загрузите все файлы проекта.
3. Сделай первый commit и push.

## Деплой на Railway

1. Создай новый проект в Railway.
2. Выбери Deploy from GitHub Repo.
3. Подключи этот репозиторий.
4. Добавь переменную окружения:
   - `TELEGRAM_BOT_TOKEN`
5. Railway сам подхватит:
   - `Procfile`
   - `railway.toml`

## Важно

Сейчас:
- бот работает через polling
- прогресс хранится в памяти
- после перезапуска прогресс сбросится

Следующий этап можно сделать таким:
- хранение прогресса в Redis/PostgreSQL
- чтение PDF/DOCX/JPG
- интеграция с OpenAI API
- inline-викторины с вариантами ответов
