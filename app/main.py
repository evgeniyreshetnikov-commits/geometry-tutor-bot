import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from .handlers import start, callbacks, handle_photo, handle_document, handle_text


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Укажи TELEGRAM_BOT_TOKEN в переменных окружения.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
