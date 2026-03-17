# Geometry 7 Class Telegram Bot

Телеграм-бот по геометрии 7 класса.

Что умеет:
- не даёт готовые решения;
- помогает найти идею задачи;
- разбирает доказательство по шагам;
- принимает PDF, DOCX, JPG, PNG;
- даёт тренировку, викторину, задание дня;
- показывает прогресс и достижения в рамках текущего запуска.

## Запуск в Railway

1. Создайте бота через @BotFather.
2. Загрузите файлы в GitHub.
3. В Railway создайте проект из GitHub-репозитория.
4. Во вкладке Variables добавьте:
   - `BOT_TOKEN` = токен от BotFather
5. Если нужно распознавание JPG/PNG, добавьте переменную:
   - `RAILPACK_DEPLOY_APT_PACKAGES` = `tesseract-ocr tesseract-ocr-rus`
6. В Start Command укажите:
   - `python bot.py`
7. Нажмите Deploy.

## Команды
- `/start`
- `/help`
- `/topics`
- `/parents`
- `/progress`
- `/daily`

## Важно
Без внешней базы прогресс может сбрасываться после нового деплоя Railway.
