from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters
from services.date_service import add_date  # Импортируем функцию
from datetime import datetime

user_states = {}


async def say_hi(update, context):
    chat = update.effective_chat
    chat_id = update.message.chat.id
    if chat_id == 792230644:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, Алена, есть новые даты?')
    else:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Привет, я бот для записи!')


async def wake_up(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup(
        [['Посмотреть свободные даты'], ['Добавить дату']])
    await context.bot.send_message(chat_id=chat.id,
                                   text='Спасибо, что включили меня',
                                   reply_markup=buttons)


async def add_date_handler(update, context):
    chat = update.effective_chat
    chat_id = update.message.chat.id
    user_states[chat_id] = 'adding_date'
    await context.bot.send_message(chat_id=chat.id,
                                   text='Пожалуйста, введите дату и время в формате DD.MM HH:MM.')


async def handle_date_input(update, context):
    chat = update.effective_chat
    chat_id = update.message.chat.id

    if user_states.get(chat_id) == 'adding_date':
        date_time = update.message.text
        name = "Неизвестно"

        try:
            date_str, time_str = date_time.split()
            result_message = add_date(date_str, time_str,
                                      name)  # Используем новую функцию

            if "Ошибка" in result_message:
                await context.bot.send_message(chat_id=chat.id,
                                               text=result_message)
                # Не сбрасываем состояние, чтобы пользователь мог попробовать снова
                return

            await context.bot.send_message(chat_id=chat.id, text=result_message)
            user_states[
                chat_id] = None  # Сбрасываем состояние только при успешном добавлении
        except ValueError:
            await context.bot.send_message(chat_id=chat.id,
                                           text='Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM.')
            # Не сбрасываем состояние, чтобы пользователь мог попробовать снова

    else:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Сначала нажмите "Добавить дату".')


def setup_handlers(application):
    application.add_handler(CommandHandler('start', wake_up))
    application.add_handler(CommandHandler('add_date', add_date_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("Добавить дату"),
                       add_date_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input))