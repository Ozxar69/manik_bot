import os
import telegram
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from handlers.handlers_setup import setup_handlers


def main():
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    application = ApplicationBuilder().token(token).build()

    setup_handlers(application)

    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("Бот остановлен пользователем.")
    except telegram.error.NetworkError as e:
        print(f"Ошибка соединения {e}")


if __name__ == "__main__":
    main()
