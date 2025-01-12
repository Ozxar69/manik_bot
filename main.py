from telegram.ext import ApplicationBuilder
from handlers.bot_handlers import setup_handlers

def main():
    application = ApplicationBuilder().token(
        '5727798773:AAHZXJfbg054rdwf4mux5OeCyXj0weoBqpI').build()

    setup_handlers(application)

    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("Бот остановлен пользователем.")

if __name__ == '__main__':
    main()