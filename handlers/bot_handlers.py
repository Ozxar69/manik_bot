from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters
import pandas as pd
import os
from datetime import datetime

DATA_FILE = 'dates.csv'
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

async def add_date(update, context):
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

        if not os.path.exists(DATA_FILE):
            df = pd.DataFrame(columns=['Дата', 'Время', 'Имя', 'Подтверждение'])
            df.to_csv(DATA_FILE, index=False)

        df = pd.read_csv(DATA_FILE)

        try:
            current_year = datetime.now().year
            date_str, time_str = date_time.split()
            date_with_year = f"{date_str}.{current_year}"
            new_entry = pd.DataFrame(
                {'Дата': [date_with_year], 'Время': [time_str], 'Имя': [name],
                 'Подтверждение': [0]})
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)

            await context.bot.send_message(chat_id=chat.id,
                                           text='Дата успешно добавлена!')
        except ValueError:
            await context.bot.send_message(chat_id=chat.id,
                                           text='Ошибка формата. Пожалуйста, введите дату и время в формате DD.MM HH:MM.')

        user_states[chat_id] = None
    else:
        await context.bot.send_message(chat_id=chat.id,
                                       text='Сначала нажмите "Добавить дату".')

def setup_handlers(application):
    application.add_handler(CommandHandler('start', wake_up))
    application.add_handler(CommandHandler('add_date', add_date))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("Добавить дату"), add_date))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input))
