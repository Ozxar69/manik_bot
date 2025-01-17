import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from handlers.bot_handlers import setup_handlers


def main():
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    application = ApplicationBuilder().token(token).build()

    setup_handlers(application)

    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("Бот остановлен пользователем.")


if __name__ == "__main__":
    main()
